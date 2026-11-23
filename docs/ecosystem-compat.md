# 生态兼容性：OpenMausBot 与 dsbot

> 核查日期：2026-11-22。以下结论来自 GitHub 仓库检索 + 读取对方仓库的 `README.md` 与一个 playbook 实例（`packages/engineering.md`），**未安装、未运行这两个项目**。

## 结论速览

| 项目 | 适配本模式（1主4子 + 关键词路由） | 用法 |
| --- | --- | --- |
| **OpenMausBot** `milind-soni/OpenMausBot` | **部分适配**：它的 playbook 是「单 Markdown + YAML frontmatter」，与本仓库的 SKILL.md 同构，可直接产出可导入包；官方提供 macOS / Windows x64 / Linux 三平台构建 | 用 [`packages/short-drama-crew.md`](../packages/short-drama-crew.md) 作为 team playbook 交给它的 Chief of Staff |
| **dsbot** `zylzyqzz/dsbot` | **不适配**：它不是 bot 编排框架，而是把 DeepSeek Harness（DSH）变成手机 PWA 的接入网关 | 可作为「在手机上访问 DSH」的壳；DSH 本身的 skill 机制与本仓库的对接另行确认 |

## OpenMausBot

**实测到的仓库信息**（GitHub Search API，2026-11-22）：

- `milind-soni/OpenMausBot` — stars 26,856、TypeScript、最近推送 2026-11-23、Apache-2.0
- 自我描述：Open-source Grok Bot alternative with a virtual machine
- 同生态：`milind-soni/openmausbot-teams`（社区 team 模板与 skill playbooks，115 stars）、`milind-soni/openmausbot-releases`（签名与公证的 macOS 构建）

**它的运行形态**（来自 README）：

- 桌面应用，官方分发 `.dmg`（Apple silicon 与 Intel 两个包）——**官方只面向 macOS**
- 数据落在本地 `~/.openmausbot`，不经过云端
- 每个 bot 可单独指定模型、单独的电脑（云 Linux 桌面 / 本地 VM / 本机），可接 Composio 的 500+ 应用
- 有「Chief of Staff」入口，用来接收 playbook

**两者的格式为什么能对上**：

`openmausbot-teams` 里每个 playbook 就是一个普通 Markdown 文件，frontmatter 字段为
`botmrr / id / release / name / tagline / summary / category / author / license / featured / tags / outcomes / setupMinutes / requirements`，
正文用 `## Activation / ## Mission / ## Outcomes / ## Connections / ## Team` 组织，每个 agent 一个 `###` 小节。

这与本仓库的 `skills/*/SKILL.md`（`name` + `description` frontmatter）结构一致，所以
[`packages/short-drama-crew.md`](../packages/short-drama-crew.md) 按该格式把「1 主 4 子 + 50 条路由」压成单文件，
交给对方的 Chief of Staff 即可读取；对方看不懂文件系统时，直接把 `prompt-router.md` 与相关
`prompt-templates.md` 小节贴进对话也能工作。

**限制**：

- **Windows 可用**。最新 release `v0.1.177` 的实际资产：`OpenMausBot-0.1.177-setup.exe`（Windows x64）、`arm64.dmg` / `x64.dmg`（macOS）、`amd64.deb` / `x86_64.rpm` / `x86_64.AppImage`（Linux）。
  Windows 安装包**尚未代码签名**，SmartScreen 会提示「未知发布者」，需点「更多信息 → 仍要运行」；默认安装到 `%LOCALAPPDATA%\Programs\OpenMausBot`，不要手动搬目录（后续更新会回到安装器记录的路径）。
- 它是「多 bot 各带一台电脑」的重型桌面形态（Electron），与本仓库「纯文件 + 可选 CLI 工具」的轻量定位不同，不需要为了用本模式去装它。

## dsbot

**实测到的仓库信息**：

- `zylzyqzz/dsbot` — stars 4、JavaScript、最近推送 2026-10-26
- 自我描述：Complete mobile PWA for DeepSeek Harness (DSH)，当前 `0.3.0`，对齐 DSH `0.2.x`（`engines.dsh: ">=0.2.0 <0.3.0"`）
- 基于 MIT 的 `dsh-mobile-gate` 做增强

**它做什么**：给自建 DSH 套一层安全网关 + PWA 壳，让手机能远程访问、加到主屏、离线可用、带通知与触屏手势。

**为什么不适配**：它解决的是「访问层」（怎么在手机上打开 DSH），不涉及「编排层」（怎么把需求拆给多个角色、怎么路由提示词）。把本仓库塞进它没有意义；正确的关系是——**如果**你在用 DSH，DSbot 让你能在手机上打开 DSH，而本仓库的 skill 作为 DSH 内的能力被加载。DSH 侧的 skill 加载机制本次**未核实**。

## 未验证的部分

1. OpenMausBot 是否接受 `skills/` 目录结构、是否读 `AGENTS.md`/`CLAUDE.md` —— 只验证了 playbook 文件格式，**未验证实际导入**。
2. OpenMausBot 从源码在 Windows 上构建的可行性 —— 未尝试。
3. DSH（DeepSeek Harness）的 skill / 多 agent 机制、以及 DSBot 与它的插件接口 —— 未读源码。
4. 两个项目的实际运行效果与 Star 数是否匹配 —— 未做深度审计。
