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
├── tools/                           # 生图 / 生视频 / FFmpeg 粗剪 / MCP Server
├── .env.example                     # 引擎密钥模板（复制为 .env 后填写）
└── skills/                          # 6 个核心 Skill（主控路由 + 5大短剧知识库）
```

## 音视频自动出片引擎（即梦 / 可灵 / 百炼 / 本地模型 + FFmpeg）

纯文本 Bot 通过调用 `tools/` 下的 CLI 脚本或 `tools/mcp_server.py`，即可端到端生成图片、单镜视频并自动剪辑合成 MP4：

1. **安装依赖与配置环境**
   ```bash
   pip install -r tools/requirements.txt
   cp .env.example .env
   ```
2. **切换后端引擎（改 `.env`）**
   - `mock`：默认干跑模式，无需任何 API Key，用 FFmpeg 占位画面跑通全流程
   - `bailian`：阿里云百炼（通义万相），异步提交 + 轮询取图
   - `jimeng`：火山引擎 / 即梦
   - `kling`：可灵 AI
   - `local`：本地部署模型（ComfyUI / 自建 REST）
3. **命令行直接调用**
   ```bash
   python tools/gen_image.py --prompt "雨夜公寓门口" --out workspace/ep01/shot_01.png
   python tools/gen_video.py --prompt "钥匙插入锁孔" --first-frame workspace/ep01/shot_01.png --out workspace/ep01/shot_01.mp4 --duration 2
   python tools/render_cut.py --clips workspace/ep01/shot_01.mp4 workspace/ep01/shot_02.mp4 --out workspace/ep01/final.mp4 --bgm bgm.mp3
   ```
4. **MCP 挂载（可选）**：`python tools/mcp_server.py`，把生图、生视频、粗剪暴露为 Bot 原生工具（需 `pip install fastmcp`）。

> 引擎能力差异：
> - `mock` / `local`：无需外网，直接产出文件（mock 用 FFmpeg 占位画面）。
> - `bailian` / `kling` / `jimeng`：均为「提交 → 轮询 → 下载」完整实现，会把平台产物落盘到 `--out`。
> - 鉴权：百炼用 `BAILIAN_API_KEY`；可灵需 `KLING_ACCESS_KEY` + `KLING_SECRET_KEY`（内部签 HS256 JWT）；即梦官方视觉 API 需 `JIMENG_ACCESS_KEY` + `JIMENG_SECRET_KEY`（HMAC-SHA256 签名），只填 `JIMENG_API_KEY` 时走 Bearer，仅适用于自建中转。
> - 即梦的 `req_key` 与返回字段随模型变化，可用 `JIMENG_IMAGE_REQ_KEY` / `JIMENG_VIDEO_REQ_KEY` / `JIMENG_API_VERSION` 覆盖，不必改代码。
>
> 已验证范围：`mock` 端到端实跑；三家异步协议用本地 mock 服务验证了提交、多轮轮询、产物下载与失败分支。**真实平台调用尚未用有效密钥验证**，首次接入请先用一条低成本的图测试。

## 许可证

MIT，见 LICENSE。



