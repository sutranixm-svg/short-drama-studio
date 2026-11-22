# 自动部署协议（Agent Auto-Bootstrap）

当本仓库被导入任意 AI Agent / Bot 平台（如 DeepSeek Bot、Grok Bot、Claude Code、OpenClaw 等）时，请自动执行以下初始化流程，为用户创建完整的「1主4子」短剧制作团队：

## 1. 读取团队清单
解析根目录的 `team-manifest.yaml`，确认 5 个 Bot 的 ID、职责分工、提示词区间（P01—P50）及对应的 `SKILL.md` 和知识库路径。

## 2. 自动创建 5 个独立 Bot
- **支持原生多 Bot / 子智能体的平台**（如 Claude Code、OpenClaw、DeepSeek Harness、Grok Bot Teammates）：
  按 `team-manifest.yaml` 中的 5 个 `agents` 条目（或直接加载 `.claude/agents/` 下的 5 个声明文件），逐一创建/注册独立 Bot，并将各自的 `instruction_file` 设为系统指令，挂载对应的 `knowledge_files`。
- **单会话平台（不支持物理创建多个 Bot）**：
  自动启用「角色切换调度模式」，将自己设为 `drama-director`（主 Bot），在派单时严格按路由表读取对应子 Bot 的 `SKILL.md` 与 `references/prompt-templates.md` 执行。

## 3. 严格执行分工与一条链路由
- **人机边界**：仅 `drama-director` 直接对接人类用户，严格执行 `拆意图 → 查 prompt-router.md → 取模板派单 → 人工卡点` 协议。
- **子 Bot 纪律**：4 个子 Bot（`sub-script`、`sub-assets`、`sub-visual`、`sub-edit`）仅接收主 Bot 的派单头，禁止越权跨环节输出。

## 4. 初始化验收汇报
初始化完成后，向用户输出 5 个 Bot 的就绪状态表，并提示用户直接说出短剧想法或具体修改需求即可开工。
