# hermes-skill-audit

[English](README.md) | 中文

审计 & 优化 [Hermes Agent](https://github.com/NousResearch/hermes-agent) skills — 检测重复、估算 token 浪费、生命周期管理。

## 背景

Hermes Agent 会在每次对话时将**所有已安装的 skills** 加载到 system prompt 中。这是设计如此 — 让 agent 知道有哪些可用流程，按需加载。

但随着 skills 不断累积，隐藏成本也随之而来：

- **每条消息**都要为完整的 skill 列表支付 token 费用
- **重复/重叠的 skills** 浪费上下文窗口空间
- **过时的 skills**（不再相关）增加噪音但没有价值
- **没有内置工具**来检测这些问题

## 问题现状

来自 Hermes Agent 社区的反馈：

| Issue | 作者 | 情况 |
|-------|------|------|
| [#13534](https://github.com/NousResearch/hermes-agent/issues/13534) | @fengcwf | 146+ skills → ~4,400 tokens/轮 → ~8000万 tokens/年浪费 |
| [#11425](https://github.com/NousResearch/hermes-agent/issues/11425) | @LehaoLin | 89+ skills → 无法追踪使用情况或检测过期 |

两个 issue 描述了同一个核心问题：**skills 无限增长，没有反馈循环来管理它们。**

## 现有工具

Hermes Agent 提供基础的 skill 管理命令：

| 命令 | 功能 |
|------|------|
| `hermes skills list` | 列出已安装 skills |
| `hermes skills check` | 检查更新 |
| `hermes skills update` | 更新过时的 skills |
| `hermes skills uninstall` | 删除 skill |
| `hermes skills audit` | 仅安全扫描 |

**缺失功能：**
- ❌ 重复/重叠检测
- ❌ Token 使用量估算
- ❌ 使用频率追踪（哪些 skills 实际被加载了？）
- ❌ 过期 skill 检测
- ❌ 合并/整合建议
- ❌ 创建前验证（这个 skill 是否冗余？）

## 解决方案

**hermes-skill-audit** 是一个 CLI 工具：

1. **扫描** `~/.hermes/skills/` 中的所有已安装 skills
2. **分析**每个 skill 的描述、标签和内容重叠度
3. **估算**每个 skill 的 token 消耗和总量
4. **检测**重复、近似重复和过时 skills
5. **推荐**操作：保留、合并、删除或归档
6. **生成**人类可读的审计报告

### 输出示例

```
==================================================
  HERMES SKILL AUDIT REPORT
==================================================

Total skills: 112
Estimated tokens per turn: ~299,320

--------------------------------------------------
  POTENTIAL DUPLICATES
--------------------------------------------------
  🔴 automated-market-research ↔ product-market-research
     Score: 0.65 | Desc: 0.45 | Tags: 0.92 | Name: 0.75
     Tokens: 2,440 + 2,498 = 4,938

--------------------------------------------------
  RECOMMENDATIONS
--------------------------------------------------
  1. Review duplicate skills for merging:
     - Merge automated-market-research + product-market-research → save ~2,440 tokens/turn
  💡 Potential savings: ~2,440 tokens/turn
```

## 安装

```bash
# 克隆到 skills 目录
git clone https://github.com/zhangluka/hermes-skill-audit ~/.hermes/skills/hermes-skill-audit

# 运行
python3 ~/.hermes/skills/hermes-skill-audit/scripts/audit.py
```

## 使用方法

```bash
# 直接运行
python3 ~/.hermes/skills/hermes-skill-audit/scripts/audit.py

# 或者在 Hermes 会话中加载 skill
/hermes-skill-audit
```

## 配置

编辑 `scripts/audit.py` 调整参数：

- `SIMILARITY_THRESHOLD`（默认：0.6）— 重复检测灵敏度
- `TOKENS_PER_CHAR`（默认：0.25）— token 估算比率

## 路线图

- [x] v0.1 — 基础审计：列出 skills、估算 token、检测明显重复
- [ ] v0.2 — 使用频率追踪集成
- [ ] v0.3 — `--fix` 参数自动清理
- [ ] v0.4 — 创建前验证钩子
- [ ] v0.5 — 集成到 `hermes skills audit` 命令

## 贡献

这是一个社区工具，欢迎 PR。

## 许可证

MIT
