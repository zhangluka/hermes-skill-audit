---
name: hermes-skill-audit
description: >
  Audit & optimize Hermes Agent skills — detect duplicates, estimate token waste,
  and get actionable recommendations to reduce context window bloat.
version: 0.1.0
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

## What It Does

1. **Scans** all SKILL.md files in `~/.hermes/skills/`
2. **Estimates** token consumption per skill (~4 chars/token)
3. **Detects** duplicates via description + tag + name similarity
4. **Flags** low-quality skills (short/empty descriptions)
5. **Reports** actionable recommendations with potential savings

## Output

```
==================================================
  HERMES SKILL AUDIT REPORT
==================================================

Total skills: 110
Estimated tokens per turn: ~297,562

--------------------------------------------------
  POTENTIAL DUPLICATES
--------------------------------------------------
  🔴 automated-market-research ↔ product-market-research
     Score: 0.65 | Desc: 0.45 | Tags: 0.92 | Name: 0.75

--------------------------------------------------
  RECOMMENDATIONS
--------------------------------------------------
  1. Review duplicate skills for merging
  💡 Potential savings: ~15,776 tokens/turn
```

## Installation

```bash
# Clone to skills directory
git clone https://github.com/zhangluka/hermes-skill-audit ~/.hermes/skills/hermes-skill-audit

# Run
python3 ~/.hermes/skills/hermes-skill-audit/scripts/audit.py
```

## Configuration

Edit `scripts/audit.py` to adjust:

- `SIMILARITY_THRESHOLD` (default: 0.6) — duplicate detection sensitivity
- `TOKENS_PER_CHAR` (default: 0.25) — token estimation ratio

## Roadmap

- [ ] v0.2 — Usage tracking integration
- [ ] v0.3 — `--fix` flag for auto-cleanup
- [ ] v0.4 — Pre-creation validation hook
- [ ] v0.5 — Integration with `hermes skills audit`
