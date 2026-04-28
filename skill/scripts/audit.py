#!/usr/bin/env python3
"""
hermes-skill-audit v0.1
Audit Hermes Agent skills — detect duplicates, estimate token waste.
"""

import os
import re
import sys
from pathlib import Path
from collections import defaultdict
from difflib import SequenceMatcher

# --- Config ---
HERMES_SKILLS_DIR = Path.home() / ".hermes" / "skills"
TOKENS_PER_CHAR = 0.25  # ~4 chars per token (rough estimate)
SIMILARITY_THRESHOLD = 0.6  # >60% = potential duplicate


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
                })
    
    return sorted(duplicates, key=lambda x: x['score'], reverse=True)


def find_stale(skills: list, days_threshold: int = 30) -> list:
    """Find skills that might be stale (placeholder — needs usage tracking)."""
    # v0.1: Flag skills with very generic/empty descriptions
    stale = []
    for skill in skills:
        if not skill['description'] or len(skill['description']) < 20:
            stale.append(skill)
    return stale


def generate_report(skills: list, duplicates: list, stale: list) -> str:
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
    lines.append(f"Estimated yearly cost (1000 turns/day): ~{total_tokens * 1000 * 365:,} tokens")
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
            lines.append(f"    - {s['name']} (~{s['estimated_tokens']:,} tokens)")
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
    lines.append("  LOW-QUALITY / STALE")
    lines.append("-" * 50)
    if stale:
        for s in stale:
            lines.append(f"  🟡 {s['name']} — description: '{s['description'][:50]}...'")
    else:
        lines.append("  ✅ All skills have adequate descriptions")
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
        lines.append(f"  2. Review {len(stale)} low-quality skills for cleanup")
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
    skills_dir = HERMES_SKILLS_DIR
    
    if not skills_dir.exists():
        print(f"Error: Skills directory not found: {skills_dir}")
        sys.exit(1)
    
    print(f"Scanning {skills_dir}...")
    skills = scan_skills(skills_dir)
    print(f"Found {len(skills)} skills\n")
    
    duplicates = find_duplicates(skills)
    stale = find_stale(skills)
    
    report = generate_report(skills, duplicates, stale)
    print(report)


if __name__ == '__main__':
    main()
