# hermes-skill-audit

English | [中文](README_CN.md)

[![Version](https://img.shields.io/badge/version-0.5.0-blue.svg)](https://github.com/zhangluka/hermes-skill-audit)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/zhangluka/hermes-skill-audit/blob/main/LICENSE)
[![Hermes Agent](https://img.shields.io/badge/Hermes-Agent-6C3483.svg)](https://github.com/NousResearch/hermes-agent)

> **Stop burning tokens on skills you never use.**

Audit & optimize [Hermes Agent](https://github.com/NousResearch/hermes-agent) skills — detect duplicates, estimate token waste, track usage, and auto-cleanup.

---

## The Problem

Hermes Agent loads **every installed skill** into the system prompt on every conversation. As skills accumulate, so does the cost:

| Metric | Impact |
|--------|--------|
| 110+ skills | ~300,000 tokens wasted per turn |
| No usage tracking | Can't tell which skills are actually used |
| No duplicate detection | Same knowledge stored multiple times |
| No cleanup mechanism | Skills grow unbounded forever |

### Real-World Impact

> I burned through **60 million credits in 10 hours**. My token plan was exhausted before I even realized what happened. After investigation, I found Hermes's uncontrolled skill management was a major contributor — 110+ skills loaded into every single message, most of them never actually used, many duplicated.
>
> — [@zhangluka](https://github.com/zhangluka)

### Community Reports

| Issue | Author | Situation |
|-------|--------|-----------|
| [#13534](https://github.com/NousResearch/hermes-agent/issues/13534) | @fengcwf | 146+ skills → ~4,400 tokens/turn → ~80M tokens/year |
| [#11425](https://github.com/NousResearch/hermes-agent/issues/11425) | @LehaoLin | 89+ skills → no usage tracking, no cleanup |

---

## Solution

**hermes-skill-audit** is a CLI tool that brings visibility and control to your skill library.

### Features

| Feature | v0.1 | v0.2 | v0.3 | v0.4 | v0.5 |
|---------|------|------|------|------|------|
| Scan all skills | ✅ | ✅ | ✅ | ✅ | ✅ |
| Token estimation | ✅ | ✅ | ✅ | ✅ | ✅ |
| Duplicate detection | ✅ | ✅ | ✅ | ✅ | ✅ |
| Usage tracking | ❌ | ✅ | ✅ | ✅ | ✅ |
| Auto-cleanup (`--fix`) | ❌ | ❌ | ✅ | ✅ | ✅ |
| Pre-creation validation | ❌ | ❌ | ❌ | ✅ | ✅ |
| JSON output | ❌ | ❌ | ❌ | ❌ | ✅ |

### Quick Start

```bash
# Clone
git clone https://github.com/zhangluka/hermes-skill-audit ~/.hermes/skills/hermes-skill-audit

# Run audit
python3 ~/.hermes/skills/hermes-skill-audit/scripts/audit.py
```

### Sample Output

```
==================================================
  HERMES SKILL AUDIT REPORT
==================================================

Total skills: 112
Estimated tokens per turn: ~299,443
Tracked skills: 0

--------------------------------------------------
  POTENTIAL DUPLICATES
--------------------------------------------------
  🔴 automated-market-research ↔ product-market-research
     Score: 0.65 | Tags: 0.92 | Name: 0.75
     Tokens: 2,440 + 2,498 = 4,938

--------------------------------------------------
  RECOMMENDATIONS
--------------------------------------------------
  1. Review duplicate skills for merging
  💡 Potential savings: ~2,440 tokens/turn
```

---

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

---

## Configuration

Edit `scripts/audit.py` to adjust:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `SIMILARITY_THRESHOLD` | 0.6 | Duplicate detection sensitivity (0.0-1.0) |
| `TOKENS_PER_CHAR` | 0.25 | Token estimation ratio (~4 chars/token) |
| `STALE_DAYS` | 30 | Days without use to be considered stale |

---

## Roadmap

- [x] v0.1 — Basic audit: list skills, estimate tokens, detect duplicates
- [x] v0.2 — Usage tracking integration (`--record`)
- [x] v0.3 — Auto-cleanup with `--fix` and `--dry-run`
- [x] v0.4 — Pre-creation validation (`--validate`)
- [x] v0.5 — JSON output, summary mode, advanced reporting

---

## Contributing

This is a community tool. PRs welcome.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT — see [LICENSE](LICENSE) for details.

---

<div align="center">
  <sub>Built with ❤️ by <a href="https://github.com/zhangluka">@zhangluka</a></sub>
</div>
