# Short Drama Studio

> AI 短剧多智能体制作团队：**1 个总控 + 4 个专业 Bot + 50 条提示词**，支持从剧本、资产、分镜到剪辑的完整制作链路。

本项目是一个可移植的文件型团队配置，适用于 Claude Code、OpenClaw、DeepSeek Bot、Grok Bot 及其他支持 Skill / Agent 的平台。它不绑定单一模型或生成平台：可以只用提示词和外部软件制作，也可以选配本地或云端音视频引擎自动出片。

## 你能用它做什么

- **剧本**：诊断剧本、完善人物动机、升级冲突、优化对白和结尾钩子（P01—P10）
- **美术资产**：角色三视图、表情与服装状态、场景基准图、道具和视觉风格板（P11—P20）
- **分镜与提示词**：九镜头 15 秒分镜、首尾帧、图生视频、口型与局部修图提示词（P21—P40）
- **剪辑与配乐**：粗剪顺序、对白节奏、独白音轨、音效、配乐、字幕和交付检查（P41—P50）
- **可选自动出片**：通过 `mock`、即梦、可灵、阿里百炼或本地模型生成图片、视频并用 FFmpeg 拼接

## 团队架构

```text
人类用户
   │
   ▼
drama-director（总控：拆意图 → 查路由 → 取模板派单 → 人工卡点）
   ├── sub-script  · 剧本完善与诊断       · P01—P10
   ├── sub-assets  · 角色、场景与道具设定   · P11—P20
   ├── sub-visual  · 分镜与图片/视频提示词  · P21—P40
   └── sub-edit    · 剪辑、配乐与交付       · P41—P50
```

只有 `drama-director` 直接面向用户；专业 Bot 由总控按路由表派单，避免跨环节输出和上下文混乱。团队的唯一真相源是 [`team-manifest.yaml`](team-manifest.yaml)。

## 快速开始

### 方式一：导入 Agent 平台

```bash
git clone https://github.com/sutranixm-svg/short-drama-studio.git
cd short-drama-studio
bash adapters/install.sh
```

安装脚本会将 6 个 Skill 和 5 个 Bot 声明注册到已检测到的 Claude Code / OpenClaw 用户目录。也可以显式指定目标：

```bash
bash adapters/install.sh --claude
bash adapters/install.sh --openclaw
```

完成后，在 Agent 中输入 **“初始化短剧团队”**，或直接描述你的短剧需求。

其他导入方式：

- **DeepSeek Bot / DSH**：使用 [`adapters/deepseek-bot/index.json`](adapters/deepseek-bot/index.json) 中的团队预设。
- **Grok Bot 或通用 Agent**：让 Agent 读取 [`AGENTS.md`](AGENTS.md)、[`team-manifest.yaml`](team-manifest.yaml) 和 [`adapters/grok-bot/team.json`](adapters/grok-bot/team.json)。
- **单会话平台**：无法创建独立子 Bot 时，按 [`skills/drama-director/references/prompt-router.md`](skills/drama-director/references/prompt-router.md) 启用角色切换调度模式。

### 方式二：只使用提示词

不需要 API Key，也不需要安装 Python。直接从对应的 `references/prompt-templates.md` 复制模板，在即梦、可灵等外部平台生成素材：

1. 用 `skills/drama-assets/` 生成角色、场景和道具基准资产；
2. 用 `skills/drama-shots/` 与 `skills/drama-prompts/` 生成分镜、首帧和单镜视频提示词；
3. 按 `CHAR_001_v01.png`、`shot_03_v01.mp4` 等格式保存到 `workspace/`；
4. 按 [`docs/acceptance-checklist.md`](docs/acceptance-checklist.md) 验收，再进行剪辑。

这是推荐的低门槛路径：生成在外部平台完成，仓库负责提示词、资产一致性和交付流程。

## 自动出片（可选）

### 1. 安装依赖并配置引擎

```bash
python -m pip install -r tools/requirements.txt
cp .env.example .env
```

默认使用 `mock`，不需要任何密钥，可用占位素材跑通流程。真实平台调用前，先在 `.env` 中设置：

```dotenv
IMAGE_PROVIDER=mock
VIDEO_PROVIDER=mock
```

可用后端：

| 后端 | 用途 | 鉴权 |
| --- | --- | --- |
| `mock` | 本地干跑和流程测试 | 无 |
| `bailian` | 阿里云百炼 / 通义万相 | `BAILIAN_API_KEY` |
| `jimeng` | 火山引擎 / 即梦 | AK/SK 或中转 API Key |
| `kling` | 可灵 AI | `KLING_ACCESS_KEY` + `KLING_SECRET_KEY` |
| `local` | ComfyUI 或自建 REST 服务 | 按本地服务配置 |

### 2. 生成图片、视频并拼接

```bash
python tools/gen_image.py \
  --prompt "雨夜公寓门口，电影感，竖屏 9:16" \
  --out workspace/ep01/shot_01.png

python tools/gen_video.py \
  --prompt "钥匙缓慢插入锁孔，镜头轻微推进" \
  --first-frame workspace/ep01/shot_01.png \
  --out workspace/ep01/shot_01.mp4 \
  --duration 2

python tools/render_cut.py \
  --clips workspace/ep01/shot_01.mp4 workspace/ep01/shot_02.mp4 \
  --out workspace/ep01/final.mp4 \
  --bgm bgm.mp3
```

也可以用 `--provider mock|jimeng|kling|bailian|local` 临时覆盖 `.env` 配置。需要将生成能力暴露为 Bot 工具时，可选安装 `fastmcp` 后运行：

```bash
python tools/mcp_server.py
```

> 已验证：`mock` 端到端流程，以及三家异步协议的本地 mock 服务测试。真实平台需要有效密钥，首次接入建议先用低成本请求测试。

## 素材验收

生成图片或视频后，不要只按文字描述判断“通过”。使用 [`docs/acceptance-checklist.md`](docs/acceptance-checklist.md) 对照实际文件检查：

- 角色身份、服装、左右特征和状态是否连续；
- 场景结构、光源和机位是否符合剧本；
- 首尾帧、动作、口型和时长是否可衔接；
- 最终判定为 **可留用 / 需修改 / 需重生成**。

## 项目结构

```text
.
├── team-manifest.yaml           # 5 个 Bot 的唯一真相源
├── skills/                      # 总控路由与 5 个专业 Skill
├── .claude/agents/              # 5 个独立 Bot 声明
├── adapters/                    # 各平台适配文件与安装脚本
├── packages/                    # 可移植 team playbook
├── tools/                       # 生图、生视频、MCP 和 FFmpeg 粗剪
├── docs/                        # 使用说明、兼容性与验收清单
├── .env.example                 # 音视频引擎配置模板
└── AGENTS.md / CLAUDE.md       # 自动建团引导协议
```

## 兼容性说明

- 本项目本身是 **Markdown + YAML + JSON + Python CLI**，不要求绑定特定模型。
- OpenMausBot 可使用 [`packages/short-drama-crew.md`](packages/short-drama-crew.md) 作为 team playbook。
- `dsbot` 属于 DeepSeek Harness 的移动访问网关，不是多 Bot 编排器；它可以作为访问层，不能替代本项目的路由和团队配置。
- 详细核查范围和未验证事项见 [`docs/ecosystem-compat.md`](docs/ecosystem-compat.md)。

## 许可证

[MIT](LICENSE)
