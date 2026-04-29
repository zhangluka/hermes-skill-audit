---
name: hermes-skill-audit
description: >
  Audit & optimize Hermes Agent skills — detect duplicates, estimate token waste,
  track usage, auto-cleanup, and pre-creation validation.
version: 0.6.0
author: zhangluka
license: MIT
triggers:
  - audit skills
  - check skills
  - skill usage
  - token waste
  - duplicate skills
  - clean up skills
  - optimize skills
  - skill report
  - 审计 skills
  - 清理 skills
  - 检查重复
  - token 浪费
metadata:
  hermes:
    tags: [hermes, skills, audit, optimization, tokens, cleanup]
    related_skills: [hermes-agent]
---

# Hermes Skill Audit

Audit your installed Hermes skills to reduce token waste and keep your skill library lean.

## When to Load

- User asks to audit, check, or optimize skills
- User mentions token waste or duplicate skills
- User wants a skill usage report
- Before creating new skills (validate first)
- Periodic maintenance requests

## Quick Start

Run the audit script via terminal:

```bash
python3 ~/.hermes/skills/hermes-skill-audit/scripts/audit.py [options]
```

## Agent Workflow

### 1. Full Audit Report

When user asks for a general audit or skill report:

```bash
python3 ~/.hermes/skills/hermes-skill-audit/scripts/audit.py
```

Returns: Complete report with skills by category, duplicates, stale skills, and recommendations.

### 2. Quick Summary

When user wants a brief overview:

```bash
python3 ~/.hermes/skills/hermes-skill-audit/scripts/audit.py --summary
```

Returns: One-line summary with counts.

### 3. Check for Duplicates

When user asks about duplicate or overlapping skills:

```bash
python3 ~/.hermes/skills/hermes-skill-audit/scripts/audit.py
```

Look for "POTENTIAL DUPLICATES" section in output.

### 4. Find Stale Skills

When user asks which skills are unused or stale:

```bash
python3 ~/.hermes/skills/hermes-skill-audit/scripts/audit.py
```

Look for "STALE / LOW-VALUE" section in output.

### 5. Auto-Cleanup

When user wants to clean up duplicates and stale skills:

**Preview first (dry run):**
```bash
python3 ~/.hermes/skills/hermes-skill-audit/scripts/audit.py --dry-run
```

**Execute cleanup:**
```bash
python3 ~/.hermes/skills/hermes-skill-audit/scripts/audit.py --fix
```

Archived skills move to `~/.hermes/skills-archive/`.

### 6. Validate New Skill

Before creating a new skill, check if similar ones exist:

```bash
python3 ~/.hermes/skills/hermes-skill-audit/scripts/audit.py --validate "skill-name" "description" "tag1,tag2"
```

Returns: Validation result with conflicts, warnings, and token impact.

### 7. Record Skill Usage

When a skill is loaded/used, record it:

```bash
python3 ~/.hermes/skills/hermes-skill-audit/scripts/audit.py --record <skill-name>
```

### 8. Export Report

Save audit report to file:

```bash
python3 ~/.hermes/skills/hermes-skill-audit/scripts/audit.py --export report.txt
python3 ~/.hermes/skills/hermes-skill-audit/scripts/audit.py --json --export report.json
```

## Configuration

Edit `scripts/audit.py` to adjust:

- `SIMILARITY_THRESHOLD` (default: 0.6) — duplicate detection sensitivity
- `TOKENS_PER_CHAR` (default: 0.25) — token estimation ratio
- `STALE_DAYS` (default: 30) — days without use to be considered stale

## Output Formats

- **Text** (default): Human-readable report with emoji indicators
- **JSON**: Use `--json` flag for programmatic use

## Installation

```bash
git clone https://github.com/zhangluka/hermes-skill-audit ~/.hermes/skills/hermes-skill-audit
```

## Version History

- v0.1 — Basic audit: list skills, estimate tokens, detect duplicates
- v0.2 — Usage tracking integration
- v0.3 — `--fix` flag for auto-cleanup
- v0.4 — Pre-creation validation hook
- v0.5 — Advanced reporting (JSON, export)
- v0.6 — Natural language triggers for Agent integration

## Contributing

This is a community tool. PRs welcome.

## License

MIT
