#!/usr/bin/env python3
"""
hermes-skill-audit v0.3
Audit Hermes Agent skills — detect duplicates, estimate token waste, track usage, auto-cleanup.
"""

import os
import re
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from difflib import SequenceMatcher

# --- Config ---
HERMES_SKILLS_DIR = Path.home() / ".hermes" / "skills"
USAGE_FILE = Path.home() / ".hermes" / "skill-usage.json"
ARCHIVE_DIR = Path.home() / ".hermes" / "skills-archive"
TOKENS_PER_CHAR = 0.25  # ~4 chars per token (rough estimate)
SIMILARITY_THRESHOLD = 0.6  # >60% = potential duplicate
STALE_DAYS = 30  # Days without use to be considered stale


def load_usage_data() -> dict:
    """Load skill usage tracking data."""
    if USAGE_FILE.exists():
        try:
            return json.loads(USAGE_FILE.read_text())
        except Exception:
            return {}
    return {}


def save_usage_data(data: dict):
    """Save skill usage tracking data."""
    USAGE_FILE.parent.mkdir(parents=True, exist_ok=True)
    USAGE_FILE.write_text(json.dumps(data, indent=2))


def record_usage(skill_name: str):
    """Record that a skill was loaded/used."""
    data = load_usage_data()
    if skill_name not in data:
        data[skill_name] = {'count': 0, 'last_used': None, 'first_seen': datetime.now().isoformat()}
    data[skill_name]['count'] += 1
    data[skill_name]['last_used'] = datetime.now().isoformat()
    save_usage_data(data)


def parse_frontmatter(content: str) -> dict:
    """Parse YAML frontmatter from SKILL.md using simple line-by-line parser."""
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return {}
    
    raw = match.group(1)
    meta = {}
    current_key = None
    multiline_value = []
    in_multiline = False
    
    for line in raw.split('\n'):
        stripped = line.rstrip()
        
        # Check for top-level key: value
        top_match = re.match(r'^(\w+):\s*(.*)', stripped)
        if top_match and not line.startswith(' '):
            # Save previous multiline if any
            if in_multiline and current_key:
                meta[current_key] = ' '.join(multiline_value).strip()
                multiline_value = []
                in_multiline = False
            
            current_key = top_match.group(1)
            value = top_match.group(2).strip()
            
            # Check if it's a multiline indicator (>, |) or empty
            if value in ('>', '|'):
                in_multiline = True
            elif value:
                meta[current_key] = value
                in_multiline = False
            else:
                in_multiline = False
            continue
        
        # Nested keys (indented)
        nested_match = re.match(r'^\s+(\w+):\s*(.*)', stripped)
        if nested_match:
            # Save previous multiline if any
            if in_multiline and current_key:
                meta[current_key] = ' '.join(multiline_value).strip()
                multiline_value = []
                in_multiline = False
            
            nested_key = nested_match.group(1)
            nested_val = nested_match.group(2).strip()
            
            if nested_key == 'tags':
                tags_match = re.search(r'\[(.*)\]', nested_val)
                if tags_match:
                    meta['tags'] = [t.strip().strip("'\"") for t in tags_match.group(1).split(',')]
            elif nested_key == 'related_skills':
                rel_match = re.search(r'\[(.*)\]', nested_val)
                if rel_match:
                    meta['related_skills'] = [s.strip().strip("'\"") for s in rel_match.group(1).split(',')]
            elif nested_key == 'triggers':
                # Start of a list
                pass
            continue
        
        # Multiline content (continuation of > or |)
        if in_multiline and line.startswith(' '):
            multiline_value.append(stripped)
    
    # Save final multiline
    if in_multiline and current_key and multiline_value:
        meta[current_key] = ' '.join(multiline_value).strip()
    
    return meta


def estimate_tokens(content: str) -> int:
    """Estimate token count from content length."""
    return int(len(content) * TOKENS_PER_CHAR)


def similarity(a: str, b: str) -> float:
    """Calculate string similarity ratio."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def tag_overlap(tags_a: list, tags_b: list) -> float:
    """Calculate tag overlap ratio."""
    if not tags_a or not tags_b:
        return 0.0
    set_a = set(t.lower() for t in tags_a)
    set_b = set(t.lower() for t in tags_b)
    intersection = set_a & set_b
    union = set_a | set_b
    return len(intersection) / len(union) if union else 0.0


def scan_skills(skills_dir: Path) -> list:
    """Scan all SKILL.md files and extract metadata."""
    skills = []
    
    for skill_md in skills_dir.rglob('SKILL.md'):
        try:
            content = skill_md.read_text(encoding='utf-8')
        except Exception:
            continue
        
        meta = parse_frontmatter(content)
        if not meta.get('name'):
            # Use directory name as fallback
            meta['name'] = skill_md.parent.name
        
        # Relative path from skills dir
        rel_path = skill_md.parent.relative_to(skills_dir)
        category = rel_path.parts[0] if len(rel_path.parts) > 1 else 'root'
        
        skills.append({
            'name': meta.get('name', skill_md.parent.name),
            'description': meta.get('description', ''),
            'tags': meta.get('tags', []),
            'related_skills': meta.get('related_skills', []),
            'category': category,
            'path': str(skill_md),
            'dir_path': str(skill_md.parent),
            'content_length': len(content),
            'estimated_tokens': estimate_tokens(content),
        })
    
    return skills


def find_duplicates(skills: list) -> list:
    """Find potential duplicate/overlapping skills."""
    duplicates = []
    n = len(skills)
    
    for i in range(n):
        for j in range(i + 1, n):
            a, b = skills[i], skills[j]
            
            # Skip if same skill
            if a['name'] == b['name']:
                continue
            
            # Calculate multiple similarity signals
            desc_sim = similarity(a['description'], b['description'])
            tag_sim = tag_overlap(a['tags'], b['tags'])
            name_sim = similarity(a['name'], b['name'])
            
            # Weighted score
            score = (desc_sim * 0.5) + (tag_sim * 0.3) + (name_sim * 0.2)
            
            if score >= SIMILARITY_THRESHOLD:
                duplicates.append({
                    'skill_a': a['name'],
                    'skill_b': b['name'],
                    'score': round(score, 2),
                    'desc_sim': round(desc_sim, 2),
                    'tag_sim': round(tag_sim, 2),
                    'name_sim': round(name_sim, 2),
                    'tokens_a': a['estimated_tokens'],
                    'tokens_b': b['estimated_tokens'],
                    'path_a': a['dir_path'],
                    'path_b': b['dir_path'],
                })
    
    return sorted(duplicates, key=lambda x: x['score'], reverse=True)


def find_stale(skills: list, usage_data: dict) -> list:
    """Find skills that are stale based on usage data."""
    stale = []
    now = datetime.now()
    
    for skill in skills:
        name = skill['name']
        usage = usage_data.get(name, {})
        last_used_str = usage.get('last_used')
        
        # No usage data at all = never tracked
        if not last_used_str:
            # Check if description is very short (low quality)
            if not skill['description'] or len(skill['description']) < 20:
                skill['stale_reason'] = 'No usage data + low-quality description'
                stale.append(skill)
            continue
        
        # Parse last used date
        try:
            last_used = datetime.fromisoformat(last_used_str)
            days_since = (now - last_used).days
            
            if days_since > STALE_DAYS:
                skill['stale_reason'] = f'Not used for {days_since} days'
                skill['days_since_used'] = days_since
                skill['usage_count'] = usage.get('count', 0)
                stale.append(skill)
        except Exception:
            continue
    
    return sorted(stale, key=lambda x: x.get('days_since_used', 999), reverse=True)


def archive_skill(skill_path: str, skill_name: str) -> bool:
    """Move a skill to archive directory."""
    try:
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
        dest = ARCHIVE_DIR / skill_name
        if dest.exists():
            shutil.rmtree(dest)
        shutil.move(skill_path, str(dest))
        return True
    except Exception as e:
        print(f"  Error archiving {skill_name}: {e}")
        return False


def fix_duplicates(duplicates: list, dry_run: bool = True) -> dict:
    """Fix duplicate skills by archiving the smaller one."""
    results = {'archived': [], 'errors': []}
    
    for d in duplicates:
        # Keep the one with more tokens (presumably more complete)
        if d['tokens_a'] >= d['tokens_b']:
            keep, archive = d['skill_a'], d['skill_b']
            keep_path, archive_path = d['path_a'], d['path_b']
        else:
            keep, archive = d['skill_b'], d['skill_a']
            keep_path, archive_path = d['path_b'], d['path_a']
        
        if dry_run:
            print(f"  [DRY RUN] Would archive: {archive} (keep: {keep})")
            results['archived'].append({'name': archive, 'dry_run': True})
        else:
            if archive_skill(archive_path, archive):
                print(f"  ✅ Archived: {archive}")
                results['archived'].append({'name': archive, 'dry_run': False})
            else:
                results['errors'].append(archive)
    
    return results


def fix_stale(stale: list, dry_run: bool = True) -> dict:
    """Fix stale skills by archiving them."""
    results = {'archived': [], 'errors': []}
    
    for s in stale:
        name = s['name']
        path = s['dir_path']
        
        if dry_run:
            print(f"  [DRY RUN] Would archive: {name} — {s.get('stale_reason', '')}")
            results['archived'].append({'name': name, 'dry_run': True})
        else:
            if archive_skill(path, name):
                print(f"  ✅ Archived: {name}")
                results['archived'].append({'name': name, 'dry_run': False})
            else:
                results['errors'].append(name)
    
    return results


def generate_report(skills: list, duplicates: list, stale: list, usage_data: dict) -> str:
    """Generate human-readable audit report."""
    total_tokens = sum(s['estimated_tokens'] for s in skills)
    
    lines = []
    lines.append("=" * 50)
    lines.append("  HERMES SKILL AUDIT REPORT")
    lines.append("=" * 50)
    lines.append("")
    lines.append(f"Total skills: {len(skills)}")
    lines.append(f"Total categories: {len(set(s['category'] for s in skills))}")
    lines.append(f"Estimated tokens per turn: ~{total_tokens:,}")
    lines.append(f"Tracked skills: {len(usage_data)}")
    lines.append("")
    
    # Skills by category
    by_category = defaultdict(list)
    for s in skills:
        by_category[s['category']].append(s)
    
    lines.append("-" * 50)
    lines.append("  SKILLS BY CATEGORY")
    lines.append("-" * 50)
    for cat in sorted(by_category.keys()):
        cat_skills = by_category[cat]
        cat_tokens = sum(s['estimated_tokens'] for s in cat_skills)
        lines.append(f"  {cat} ({len(cat_skills)} skills, ~{cat_tokens:,} tokens)")
        for s in cat_skills:
            usage = usage_data.get(s['name'], {})
            count = usage.get('count', 0)
            last = usage.get('last_used', 'never')
            if last != 'never':
                last = last[:10]  # Just date part
            lines.append(f"    - {s['name']} (~{s['estimated_tokens']:,} tok, used {count}x, last: {last})")
    lines.append("")
    
    # Duplicates
    lines.append("-" * 50)
    lines.append("  POTENTIAL DUPLICATES")
    lines.append("-" * 50)
    if duplicates:
        for d in duplicates:
            lines.append(f"  🔴 {d['skill_a']} ↔ {d['skill_b']}")
            lines.append(f"     Score: {d['score']} | Desc: {d['desc_sim']} | Tags: {d['tag_sim']} | Name: {d['name_sim']}")
            lines.append(f"     Tokens: {d['tokens_a']:,} + {d['tokens_b']:,} = {d['tokens_a'] + d['tokens_b']:,}")
            lines.append("")
    else:
        lines.append("  ✅ No obvious duplicates detected")
        lines.append("")
    
    # Stale
    lines.append("-" * 50)
    lines.append("  STALE / LOW-VALUE")
    lines.append("-" * 50)
    if stale:
        for s in stale:
            reason = s.get('stale_reason', 'Unknown')
            lines.append(f"  🟡 {s['name']} — {reason}")
    else:
        lines.append("  ✅ No stale skills detected")
    lines.append("")
    
    # Recommendations
    lines.append("-" * 50)
    lines.append("  RECOMMENDATIONS")
    lines.append("-" * 50)
    
    potential_savings = 0
    if duplicates:
        lines.append("  1. Review duplicate skills for merging:")
        for d in duplicates[:3]:
            smaller = min(d['tokens_a'], d['tokens_b'])
            potential_savings += smaller
            lines.append(f"     - Merge {d['skill_a']} + {d['skill_b']} → save ~{smaller:,} tokens/turn")
    
    if stale:
        lines.append(f"  2. Review {len(stale)} stale skills for cleanup")
        stale_tokens = sum(s['estimated_tokens'] for s in stale)
        potential_savings += stale_tokens
    
    if potential_savings:
        lines.append(f"  💡 Potential savings: ~{potential_savings:,} tokens/turn")
    else:
        lines.append("  ✅ No immediate action needed")
    
    lines.append("")
    lines.append("=" * 50)
    
    return '\n'.join(lines)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Audit Hermes Agent skills')
    parser.add_argument('--record', metavar='SKILL_NAME', help='Record usage of a skill')
    parser.add_argument('--export', metavar='FILE', help='Export report to file')
    parser.add_argument('--fix', action='store_true', help='Auto-fix issues (archive duplicates and stale skills)')
    parser.add_argument('--dry-run', action='store_true', help='Show what --fix would do without actually doing it')
    args = parser.parse_args()
    
    # Record usage if requested
    if args.record:
        record_usage(args.record)
        print(f"Recorded usage: {args.record}")
        return
    
    skills_dir = HERMES_SKILLS_DIR
    
    if not skills_dir.exists():
        print(f"Error: Skills directory not found: {skills_dir}")
        sys.exit(1)
    
    print(f"Scanning {skills_dir}...")
    skills = scan_skills(skills_dir)
    print(f"Found {len(skills)} skills\n")
    
    usage_data = load_usage_data()
    duplicates = find_duplicates(skills)
    stale = find_stale(skills, usage_data)
    
    report = generate_report(skills, duplicates, stale, usage_data)
    print(report)
    
    # Fix mode
    if args.fix or args.dry_run:
        dry_run = args.dry_run or not args.fix
        print("\n" + "=" * 50)
        print("  FIX MODE" + (" (DRY RUN)" if dry_run else ""))
        print("=" * 50)
        
        if duplicates:
            print(f"\nArchiving {len(duplicates)} duplicate skills...")
            dup_results = fix_duplicates(duplicates, dry_run=dry_run)
        
        if stale:
            print(f"\nArchiving {len(stale)} stale skills...")
            stale_results = fix_stale(stale, dry_run=dry_run)
        
        print("\nDone!")
    
    if args.export:
        Path(args.export).write_text(report)
        print(f"\nReport exported to: {args.export}")


if __name__ == '__main__':
    main()
