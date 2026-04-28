---
name: hermes-skill-audit
description: >
  Audit & optimize Hermes Agent skills — detect duplicates, estimate token waste,
  track usage, auto-cleanup, and pre-creation validation.
version: 0.5.0
author: zhangluka
license: MIT
metadata:
  hermes:
    tags: [hermes, skills, audit, optimization, tokens, cleanup]
    related_skills: [hermes-agent]
---

# Hermes Skill Audit

Audit your installed Hermes skills to reduce token waste and keep your skill library lean.

## When to Use

- You have 50+ skills installed
- You notice high token usage per conversation
- You want to find duplicate or overlapping skills
- Before installing new skills (check if similar ones exist)
- Periodic maintenance (monthly recommended)

## Quick Start

```bash
python3 ~/.hermes/skills/hermes-skill-audit/scripts/audit.py
```

## Features

### v0.1 — Basic Audit
- Scan all SKILL.md files
- Estimate token consumption
- Detect duplicates via description + tag + name similarity

### v0.2 — Usage Tracking
- Record when skills are used with `--record`
- Store usage data in `~/.hermes/skill-usage.json`
- Detect stale skills based on actual usage

### v0.3 — Auto-Cleanup
- `--fix` flag to automatically archive duplicate/stale skills
- `--dry-run` mode to preview before acting
- Archived skills moved to `~/.hermes/skills-archive/`

### v0.4 — Pre-Creation Validation
- `--validate` flag to check new skill before creation
- Detect name conflicts and description overlaps
- Estimate token impact

### v0.5 — Advanced Reporting
- `--json` output for programmatic use
- `--summary` for quick overview
- Export reports with `--export`

## Usage

```bash
# Full audit report
python3 ~/.hermes/skills/hermes-skill-audit/scripts/audit.py

# Quick summary
python3 ~/.hermes/skills/hermes-skill-audit/scripts/audit.py --summary

# JSON output (for scripts/tools)
python3 ~/.hermes/skills/hermes-skill-audit/scripts/audit.py --json

# Record skill usage
python3 ~/.hermes/skills/hermes-skill-audit/scripts/audit.py --record <skill-name>

# Validate new skill before creation
python3 ~/.hermes/skills/hermes-skill-audit/scripts/audit.py --validate "name" "description" "tag1,tag2"

# Preview cleanup (dry run)
python3 ~/.hermes/skills/hermes-skill-audit/scripts/audit.py --dry-run

# Execute cleanup
python3 ~/.hermes/skills/hermes-skill-audit/scripts/audit.py --fix

# Export report
python3 ~/.hermes/skills/hermes-skill-audit/scripts/audit.py --export report.txt
python3 ~/.hermes/skills/hermes-skill-audit/scripts/audit.py --json --export report.json
```

## Configuration

Edit `scripts/audit.py` to adjust:

- `SIMILARITY_THRESHOLD` (default: 0.6) — duplicate detection sensitivity
- `TOKENS_PER_CHAR` (default: 0.25) — token estimation ratio
- `STALE_DAYS` (default: 30) — days without use to be considered stale

## Installation

```bash
# Clone to skills directory
git clone https://github.com/zhangluka/hermes-skill-audit ~/.hermes/skills/hermes-skill-audit

# Run
python3 ~/.hermes/skills/hermes-skill-audit/scripts/audit.py
```

## Roadmap

- [x] v0.1 — Basic audit: list skills, estimate tokens, detect obvious duplicates
- [x] v0.2 — Usage tracking integration
- [x] v0.3 — `--fix` flag for auto-cleanup
- [x] v0.4 — Pre-creation validation hook
- [x] v0.5 — Integration with `hermes skills audit`

## Contributing

This is a community tool. PRs welcome.

## License

MIT
