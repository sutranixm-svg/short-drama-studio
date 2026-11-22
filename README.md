# AI 短剧多智能体团队（1主4子 · 全平台一键导入）

一套开箱即用的开源多智能体短剧制作系统。导入任意主流 AI Bot 平台（**DeepSeek Bot / Grok Bot / Claude Code / OpenClaw** 等）后，自动拉起 **1 个总控主 Bot + 4 个专业子 Bot**，内置 **50 条短剧制作提示词（P01—P50）一条链关键词路由**。

## 团队架构（1主4子）

```text
人类用户
   │
   ▼
[主Bot] drama-director（总控调度：拆意图 → 查路由表 → 取模板派单 → 卡点汇报）
   ├──▶ [子Bot-1] sub-script（金牌编剧：P01—P10 剧本诊断/成稿/钩子/连续性）
   ├──▶ [子Bot-2] sub-assets（美术设定：P11—P20 三视图/表情/场景基准/道具/风格板）
   ├──▶ [子Bot-3] sub-visual（分镜与提示词：P21—P40 九镜15秒分镜/首尾帧/图生视频/口型）
   └──▶ [子Bot-4] sub-edit（剪辑与配乐：P41—P50 粗剪/对白节奏/独白音轨/配乐/交付自查）
```

## 快速导入与启动

### 1. Claude Code / OpenClaw（原生零点击）
克隆本仓库后，直接运行一键注册脚本：
```bash
git clone https://github.com/sutranixm-svg/short-drama-studio.git
cd short-drama-studio
bash adapters/install.sh
```
然后在对话中直接说：**「初始化短剧团队」** 或直接提出你的短剧需求。

### 2. DeepSeek Bot / DSH 生态
在插件发现页填入本仓库的 `adapters/deepseek-bot/index.json` 链接，一键导入整套 5 Bot 预设。

### 3. Grok Bot / 其他通用 Agent
将本仓库导入工作区，让 Agent 读取根目录的 `AGENTS.md` 与 `adapters/grok-bot/team.json`，并发送口令：
> **「请按 AGENTS.md 和 team-manifest.yaml 自动创建 5 个短剧制作 Bot，完成后向我汇报。」**

## 目录结构

```text
.
├── AGENTS.md / CLAUDE.md            # 自动建团引导协议
├── team-manifest.yaml               # 1主4子唯一真相源清单
├── .claude/agents/                  # 5 个独立 Bot 声明文件
├── adapters/                        # DeepSeek Bot / Grok Bot / 一键安装脚本
└── skills/                          # 6 个核心 Skill（主控路由 + 5大短剧知识库）
```
