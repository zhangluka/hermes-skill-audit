# hermes-skill-audit

Audit & optimize [Hermes Agent](https://github.com/NousResearch/hermes-agent) skills — detect duplicates, estimate token waste, lifecycle management.

## Background

Hermes Agent loads **all installed skills** into the system prompt on every conversation. This is by design — it enables the agent to know what procedures are available and load them on demand.

But as skills accumulate, this creates a hidden cost:

- **Every message** pays for the full skill list in tokens
- **Duplicate/overlapping skills** waste context window space
- **Stale skills** (no longer relevant) add noise without value
- **No built-in tooling** to detect these problems

## The Problem

From the Hermes Agent community:

| Issue | Author | Situation |
|-------|--------|-----------|
| [#13534](https://github.com/NousResearch/hermes-agent/issues/13534) | @fengcwf | 146+ skills → ~4,400 tokens/turn → ~80M tokens/year wasted |
| [#11425](https://github.com/NousResearch/hermes-agent/issues/11425) | @LehaoLin | 89+ skills → no way to track usage or detect staleness |

Both issues describe the same core problem: **skills grow unbounded, and there's no feedback loop to manage them.**

## Current State

Hermes Agent provides basic skill management:

| Command | What it does |
|---------|--------------|
| `hermes skills list` | List installed skills |
| `hermes skills check` | Check for updates |
| `hermes skills update` | Update outdated skills |
| `hermes skills uninstall` | Remove a skill |
| `hermes skills audit` | Security scan only |

**What's missing:**
- ❌ Duplicate / overlap detection
- ❌ Token usage estimation per skill
- ❌ Usage frequency tracking (which skills are actually loaded?)
- ❌ Stale skill detection
- ❌ Merge / consolidation suggestions
- ❌ Pre-creation validation (is this skill redundant?)

## Solution

**hermes-skill-audit** is a CLI tool that:

1. **Scans** all installed skills in `~/.hermes/skills/`
2. **Analyzes** each skill's description, tags, and content for overlaps
3. **Estimates** token consumption per skill and total
4. **Detects** duplicates, near-duplicates, and stale skills
5. **Recommends** actions: keep, merge, delete, or archive
6. **Generates** a human-readable audit report

### Output Example

```
=== Hermes Skill Audit Report ===

Total skills: 47
Estimated tokens per turn: ~3,200

🔴 DUPLICATES (3 groups):
  - "github-pr-workflow" ↔ "github-code-review" (87% overlap)
  - "nextjs-deploy" ↔ "cloudflare-pages-deploy" (62% overlap)
  - ...

🟡 STALE (>30 days unused):
  - "minecraft-modpack-server" (last used: 45 days ago)
  - ...

🟢 HEALTHY (41 skills):
  - No action needed

💡 RECOMMENDATIONS:
  1. Merge "github-pr-workflow" + "github-code-review" → save ~800 tokens/turn
  2. Archive 3 stale skills → save ~600 tokens/turn
  3. Estimated savings: ~1,400 tokens/turn (~44M tokens/year)
```

## Roadmap

- [ ] v0.1 — Basic audit: list skills, estimate tokens, detect obvious duplicates
- [ ] v0.2 — Overlap detection via description/tag similarity
- [ ] v0.3 — Integration with `hermes skills audit` command
- [ ] v0.4 — Usage tracking (requires Hermes core changes)
- [ ] v0.5 — Pre-creation validation hook

## Contributing

This is a community tool. PRs welcome.

## License

MIT
