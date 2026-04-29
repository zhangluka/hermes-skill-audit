# hermes-skill-audit

[English](README.md) | 中文

[![Version](https://img.shields.io/badge/version-0.6.0-blue.svg)](https://github.com/zhangluka/hermes-skill-audit)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/zhangluka/hermes-skill-audit/blob/main/LICENSE)
[![Hermes Agent](https://img.shields.io/badge/Hermes-Agent-6C3483.svg)](https://github.com/NousResearch/hermes-agent)

> **停止为你从不使用的 skills 浪费 token。**

审计 & 优化 [Hermes Agent](https://github.com/NousResearch/hermes-agent) skills — 检测重复、估算 token 浪费、追踪使用情况、自动清理。

---

## 问题现状

Hermes Agent 会在每次对话时将**所有已安装的 skills** 加载到 system prompt 中。随着 skills 不累累积，成本也在增长：

| 指标 | 影响 |
|------|------|
| 110+ skills | 每轮浪费 ~300,000 tokens |
| 无使用追踪 | 无法知道哪些 skills 实际被使用 |
| 无重复检测 | 相同知识存储多次 |
| 无清理机制 | Skills 无限增长 |

### 真实案例

> 我在 10 小时内烧掉了 **6000 万 Credits**。我的 token 额度在还没反应过来的时候就耗尽了。经过排查，发现 Hermes 失控的 skill 管理是主要原因 — 110+ 个 skills 被加载到每条消息中，大部分从未实际使用，还有很多是重复的。
>
> — [@zhangluka](https://github.com/zhangluka)

### 社区反馈

| Issue | 作者 | 情况 |
|-------|------|------|
| [#13534](https://github.com/NousResearch/hermes-agent/issues/13534) | @fengcwf | 146+ skills → ~4,400 tokens/轮 → ~8000万 tokens/年 |
| [#11425](https://github.com/NousResearch/hermes-agent/issues/11425) | @LehaoLin | 89+ skills → 无法追踪使用情况 |

---

## 解决方案

**hermes-skill-audit** 是一个 CLI 工具，为你的 skill 库带来可见性和控制力。

### 功能特性

| 功能 | v0.1 | v0.2 | v0.3 | v0.4 | v0.5 |
|------|------|------|------|------|------|
| 扫描所有 skills | ✅ | ✅ | ✅ | ✅ | ✅ |
| Token 估算 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 重复检测 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 使用追踪 | ❌ | ✅ | ✅ | ✅ | ✅ |
| 自动清理 (`--fix`) | ❌ | ❌ | ✅ | ✅ | ✅ |
| 创建前验证 | ❌ | ❌ | ❌ | ✅ | ✅ |
| JSON 输出 | ❌ | ❌ | ❌ | ❌ | ✅ |

### 快速开始

```bash
# 克隆
git clone https://github.com/zhangluka/hermes-skill-audit ~/.hermes/skills/hermes-skill-audit

# 运行审计
python3 ~/.hermes/skills/hermes-skill-audit/scripts/audit.py
```

### 输出示例

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

## 使用方法

```bash
# 完整审计报告
python3 ~/.hermes/skills/hermes-skill-audit/scripts/audit.py

# 快速摘要
python3 ~/.hermes/skills/hermes-skill-audit/scripts/audit.py --summary

# JSON 输出（适合脚本/工具集成）
python3 ~/.hermes/skills/hermes-skill-audit/scripts/audit.py --json

# 记录 skill 使用
python3 ~/.hermes/skills/hermes-skill-audit/scripts/audit.py --record <skill-name>

# 创建新 skill 前验证
python3 ~/.hermes/skills/hermes-skill-audit/scripts/audit.py --validate "name" "description" "tag1,tag2"

# 预览清理（dry run）
python3 ~/.hermes/skills/hermes-skill-audit/scripts/audit.py --dry-run

# 执行清理
python3 ~/.hermes/skills/hermes-skill-audit/scripts/audit.py --fix

# 导出报告
python3 ~/.hermes/skills/hermes-skill-audit/scripts/audit.py --export report.txt
python3 ~/.hermes/skills/hermes-skill-audit/scripts/audit.py --json --export report.json
```

---

## 配置

编辑 `scripts/audit.py` 调整参数：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `SIMILARITY_THRESHOLD` | 0.6 | 重复检测灵敏度 (0.0-1.0) |
| `TOKENS_PER_CHAR` | 0.25 | Token 估算比率 (~4 字符/token) |
| `STALE_DAYS` | 30 | 多少天未使用视为过期 |

---

## 路线图

- [x] v0.1 — 基础审计：列出 skills、估算 token、检测重复
- [x] v0.2 — 使用追踪集成（`--record`）
- [x] v0.3 — 自动清理（`--fix` 和 `--dry-run`）
- [x] v0.4 — 创建前验证（`--validate`）
- [x] v0.5 — JSON 输出、摘要模式、高级报告

---

## 贡献

这是一个社区工具，欢迎 PR。

1. Fork 仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 许可证

MIT — 详见 [LICENSE](LICENSE)。

---

<div align="center">
  <sub>由 <a href="https://github.com/zhangluka">@zhangluka</a> 用心构建 ❤️</sub>
</div>
