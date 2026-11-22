# 一条链关键词路由表（主 Bot 专用）

> 用途：主 Bot 收到用户大白话后，只用**关键词命中**就能锁定唯一 `提示词ID` 与 `目标子Bot`，再回源文件取完整模板派单。
> 数据来源：`50条可复制提示词.txt`（根目录）+ 五个子目录的 `references/prompt-templates.md`，全部 50 条已逐条核对，编号去重后为 P01—P50。
> 本表不含提示词正文。正文一律从 `来源文件路径` 中对应的小节标题（如 `### S01 剧本体检`）读取，禁止凭表复述。

## 架构总览：1 主 4 子

| 子Bot | 代号 | 中文名 | 对应制作环节 | 覆盖提示词 | 条数 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 子Bot-1 | `sub-script` | 金牌编剧 | 01 剧本完善与诊断 | S01—S10 → P01—P10 | 10 |
| 子Bot-2 | `sub-assets` | 美术设定 | 02 角色场景与道具 | A01—A10 → P11—P20 | 10 |
| 子Bot-3 | `sub-visual` | 分镜与提示词 | 03 分镜与镜头 + 04 图片与视频提示词 | C01—C10 → P21—P30；P01—P10 → P31—P40 | 20 |
| 子Bot-4 | `sub-edit` | 剪辑与配乐 | 05 剪辑技巧与配乐 | E01—E10 → P41—P50 | 10 |

一条链顺序：`sub-script` → `sub-assets` → `sub-visual` → `sub-edit`。

## 路由表

| 提示词ID | 提示词名称 | 触发关键词（3-5个口语/专业词） | 目标子Bot | 来源文件路径 | 核心用途一句话说明 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| P01 | S01 剧本体检 | 体检、剧本诊断、哪里弱、有没有救、帮我看看剧本 | `sub-script` | `skills/drama-script/references/prompt-templates.md` | 定位剧本薄弱点并给最小修改建议，不整篇重写。 |
| P02 | S02 故事变成可制作剧本 | 想法、写成剧本、成稿、出初稿、分场 | `sub-script` | `skills/drama-script/references/prompt-templates.md` | 把一句话创意写成可拍的分场剧本并附资产清单。 |
| P03 | S03 人物动机与关系 | 人物卡、动机、人设、为什么这么做、人物关系 | `sub-script` | `skills/drama-script/references/prompt-templates.md` | 给角色建动机卡，检查行为是否自相矛盾。 |
| P04 | S04 让冲突逐步升级 | 太平、不够燃、冲突、推进、节奏平 | `sub-script` | `skills/drama-script/references/prompt-templates.md` | 用「目标—阻碍—尝试—代价—新问题」重排节拍。 |
| P05 | S05 对白说得自然且说得完 | 台词、对白、太长、说人话、念不完 | `sub-script` | `skills/drama-script/references/prompt-templates.md` | 长台词压成能演完的短句，并给独白拆分方案。 |
| P06 | S06 分集结尾与追看理由 | 结尾、钩子、追看、悬念、下一集 | `sub-script` | `skills/drama-script/references/prompt-templates.md` | 出三种结尾方案并核对前文铺垫是否够。 |
| P07 | S07 一集拆成制作任务 | 拆任务、资产清单、编号、交给美术、CHAR | `sub-script` | `skills/drama-script/references/prompt-templates.md` | 输出 CHAR/LOC/PROP 编号资产与场次清单。 |
| P08 | S08 多集连续性核对 | 连续性、前后不一致、多集、穿帮、道具换手 | `sub-script` | `skills/drama-script/references/prompt-templates.md` | 建六列连续性表，定位跨集矛盾与修复点。 |
| P09 | S09 剧本降低制作负担 | 太贵、角色太多、减场景、可拍性、预算 | `sub-script` | `skills/drama-script/references/prompt-templates.md` | 保留剧情前提下砍制作量，给前后对照。 |
| P10 | S10 剧本修改后再检查 | 复查、改完再查、老师意见、改后验收、回归 | `sub-script` | `skills/drama-script/references/prompt-templates.md` | 比对原稿/修改稿/意见，防「修一个坏一个」。 |
| P11 | A01 人物正侧背三视图 | 三视图、正侧背、人设图、定妆、角色参考 | `sub-assets` | `skills/drama-assets/references/prompt-templates.md` | 一张图定死人物的正侧背与服装细节。 |
| P12 | A02 人物表情与情绪参考 | 表情、情绪、同一张脸、表情组、近景 | `sub-assets` | `skills/drama-assets/references/prompt-templates.md` | 同机位换表情不换脸的头肩参考组。 |
| P13 | A03 同一人物服装状态版 | 湿衣、受伤、换装、状态版、同一人 | `sub-assets` | `skills/drama-assets/references/prompt-templates.md` | 在基础定妆上只改指定状态，不新建角色。 |
| P14 | A04 场景空间基准图 | 场景、房间结构、场景基准图、平面、门在哪 | `sub-assets` | `skills/drama-assets/references/prompt-templates.md` | 先锁门窗家具位置，后面才谈换机位。 |
| P15 | A05 同一场景换机位 | 换机位、换个角度、反向、另一个视角、空间 | `sub-assets` | `skills/drama-assets/references/prompt-templates.md` | 同空间换视角，不镜像、不新增门窗。 |
| P16 | A06 道具白底与多视角参考 | 道具、白底、多视角、钥匙、物品图 | `sub-assets` | `skills/drama-assets/references/prompt-templates.md` | 单独出道具图，不带人物与手部。 |
| P17 | A07 道具损坏与使用状态 | 道具损坏、沾水、破损、版本、前后状态 | `sub-assets` | `skills/drama-assets/references/prompt-templates.md` | 同一道具做状态版本并留前后对照检查点。 |
| P18 | A08 婴儿与动物姿态约束 | 婴儿、小孩、动物、猫、抱姿 | `sub-assets` | `skills/drama-assets/references/prompt-templates.md` | 约束支撑关系与物种真实姿态，防拟人化。 |
| P19 | A09 统一视觉风格板 | 风格、统一、美术、色调统一、视觉规则 | `sub-assets` | `skills/drama-assets/references/prompt-templates.md` | 提炼全片共用的色彩、光线、材质规则。 |
| P20 | A10 资产清单与一致性检查 | 资产表、对不上、一致性、清单、混用 | `sub-assets` | `skills/drama-assets/references/prompt-templates.md` | 对照实图建资产表，指出具体哪张错在哪。 |
| P21 | C01 九镜十五秒分镜表 | 分镜、九镜、15秒、出镜头表、拆镜头 | `sub-visual` | `skills/drama-shots/references/prompt-templates.md` | 把段落剧情拆成 9 镜合计 15 秒的可执行表。 |
| P22 | C02 九宫格剧情基准图 | 九宫格、3x3、九格构图、预演、九宫格基准 | `sub-visual` | `skills/drama-shots/references/prompt-templates.md` | 3×3 九格各对应一镜的起始瞬间。 |
| P23 | C03 同一动作选择合适景别 | 景别、特写、远景、构图、拍多大 | `sub-visual` | `skills/drama-shots/references/prompt-templates.md` | 按「观众必须看懂什么」选全景/中景/近景/特写。 |
| P24 | C04 对话正反打与视线 | 正反打、对话、轴线、视线、两人聊天 | `sub-visual` | `skills/drama-shots/references/prompt-templates.md` | 守轴线排双人对话机位与视线方向。 |
| P25 | C05 发现线索的揭示镜头 | 线索、揭晓、发现、伏笔、给观众看 | `sub-visual` | `skills/drama-shots/references/prompt-templates.md` | 用「看向—细节—反应」组织揭示段落。 |
| P26 | C06 动作前后接得上 | 接不上、跳、衔接、换手、动作连不上 | `sub-visual` | `skills/drama-shots/references/prompt-templates.md` | 核对前镜尾状态与后镜起始的切点。 |
| P27 | C07 内心独白跨镜 | 独白跨镜、长独白、旁白分镜、心理 | `sub-visual` | `skills/drama-shots/references/prompt-templates.md` | 把一条独白铺到多镜的时长分配表。 |
| P28 | C08 主观镜头与人物反应 | 主观、POV、她看到、反应镜头、视点 | `sub-visual` | `skills/drama-shots/references/prompt-templates.md` | 固定视点高度做主客观镜头对。 |
| P29 | C09 运镜服务剧情 | 运镜、推镜、跟拍、横移、电影感 | `sub-visual` | `skills/drama-shots/references/prompt-templates.md` | 单镜只选一种运镜，写清起止构图。 |
| P30 | C10 镜头表拍前检查 | 拍前检查、超时、复算、复核、镜头表复核 | `sub-visual` | `skills/drama-shots/references/prompt-templates.md` | 生成前查连续性、轴线与时长算术。 |
| P31 | P01 单帧图片通用公式 | 出图、图片提示词、画一张、单帧、生成图 | `sub-visual` | `skills/drama-prompts/references/prompt-templates.md` | 把模糊审美词换成可执行的单帧提示词。 |
| P32 | P02 镜头首帧 | 首帧、第一帧、起点图、开头画面 | `sub-visual` | `skills/drama-prompts/references/prompt-templates.md` | 写「动作开始前一刻」的首帧提示词。 |
| P33 | P03 镜头尾帧 | 尾帧、最后一帧、落点、结束画面 | `sub-visual` | `skills/drama-prompts/references/prompt-templates.md` | 只改动作造成的变化，保持可接。 |
| P34 | P04 单镜视频动作与运镜 | 视频提示词、图生视频、动起来、单镜、运动 | `sub-visual` | `skills/drama-prompts/references/prompt-templates.md` | 一个主要动作＋一种运镜的 1—3 秒视频提示词。 |
| P35 | P05 现场短句与口型 | 口型、说话、对嘴、台词镜头、配音 | `sub-visual` | `skills/drama-prompts/references/prompt-templates.md` | 精确短句＋口型匹配与超时兜底方案。 |
| P36 | P06 闭嘴的内心独白 | 闭嘴、不开口、心里想、独白画面、旁白 | `sub-visual` | `skills/drama-prompts/references/prompt-templates.md` | 画面不动嘴，独白另走独立音轨。 |
| P37 | P07 没有对白的环境音与音效 | 音效、环境音、雨声、脚步声、贴声 | `sub-visual` | `skills/drama-prompts/references/prompt-templates.md` | 列声源/时点/远近的音效生成提示词。 |
| P38 | P08 光线与情绪组合 | 光线、打光、逆光、氛围、冷暖色调 | `sub-visual` | `skills/drama-prompts/references/prompt-templates.md` | 指定光源位置冷暖软硬，不堆矛盾词。 |
| P39 | P09 只修错的部分 | 修图、改一处、重画、手指、局部 | `sub-visual` | `skills/drama-prompts/references/prompt-templates.md` | 只改指定区域，给最小修改范围与检查点。 |
| P40 | P10 参考图与生成结果对照 | 对照、能不能用、留用、质检、核验 | `sub-visual` | `skills/drama-prompts/references/prompt-templates.md` | 判「可留用/需修改/需重生成」并给位置理由。 |
| P41 | E01 按剧情整理粗剪顺序 | 粗剪、拼接、顺片、剪辑顺序、串起来 | `sub-edit` | `skills/drama-edit-music/references/prompt-templates.md` | 按剧情与声音顺序出粗剪表。 |
| P42 | E02 对白剪辑与回应节奏 | 对白剪辑、接话、停顿、回应、说话节奏 | `sub-edit` | `skills/drama-edit-music/references/prompt-templates.md` | 调说话/反应停顿与画面切点。 |
| P43 | E03 一条独白跨多个镜头 | 独白音轨、一条音轨、跨镜铺、重复念 | `sub-edit` | `skills/drama-edit-music/references/prompt-templates.md` | 把一条独白音频按九镜分配区间。 |
| P44 | E04 环境音与动作音效表 | 音效表、声音表、对齐、入点、音频清单 | `sub-edit` | `skills/drama-edit-music/references/prompt-templates.md` | 五栏声音使用表＋入出点对齐。 |
| P45 | E05 为整集设计配乐简报 | 配乐、BGM、音乐、情绪曲线、整集 | `sub-edit` | `skills/drama-edit-music/references/prompt-templates.md` | 整集情绪走向与留白位置的配乐简报。 |
| P46 | E06 可复制的纯音乐生成提示词 | 生成音乐、纯音乐、无人声、乐曲、配乐提示词 | `sub-edit` | `skills/drama-edit-music/references/prompt-templates.md` | 交给音乐平台的无人声纯音乐提示词。 |
| P47 | E07 混音先让人声听得清 | 混音、听不清、人声、盖住、音量 | `sub-edit` | `skills/drama-edit-music/references/prompt-templates.md` | 人声优先的层级调整与双设备试听步骤。 |
| P48 | E08 字幕与画面重点 | 字幕、遮挡、错字、SRT、安全区 | `sub-edit` | `skills/drama-edit-music/references/prompt-templates.md` | 字幕断句、位置避让与逐句核对。 |
| P49 | E09 作品交前六项自查 | 交作业、自查、交片前、六项、成片验收 | `sub-edit` | `skills/drama-edit-music/references/prompt-templates.md` | 六维成片自查，并分清自查与正式审核。 |
| P50 | E10 成片与工程交付清单 | 交付、打包、工程文件、命名、提交 | `sub-edit` | `skills/drama-edit-music/references/prompt-templates.md` | 成片＋工程＋素材＋说明的交付清单。 |

## 冲突消解（关键词命中多个 ID 时按此判）

判序：**① 命中关键词数多者优先 → ② 用户当前所处阶段优先 → ③ 下表的「对象判据」**。

| 冲突簇 | 候选 | 对象判据 |
| :--- | :--- | :--- |
| 内心独白 | P27 / P36 / P43 | 排镜头与时长 → P27；画面不许动嘴 → P36；音轨怎么铺、避免重念 → P43 |
| 音效 | P37 / P44 | 要生成/贴出声音素材 → P37；要整理成表并对齐入出点 → P44 |
| 「检查/自查/复查」 | P01 / P10 / P20 / P30 / P40 / P49 | 剧本初查 → P01；改后回归 → P10；资产图 → P20；镜头表 → P30；生成结果 → P40；成片交付前 → P49 |
| 镜头表 vs 生成提示词 | P21 / P30 / P31—P40 | 要新拆一张表 → P21；已有表要复核 → P30；要「可直接复制的生成提示词」→ P 系列 |
| 节奏 | P04 / P42 | 剧情平、缺推进 → P04；说话接得生硬、停顿不对 → P42 |
| 光线/风格 | P19 / P38 | 定全片美术规则 → P19；给某一个镜头写光线 → P38 |
| 首尾帧 vs 单镜视频 | P32 / P33 / P34 | 只要起点图 → P32；只要落点图 → P33；要一段动起来的视频 → P34 |
| 对白/台词 | P05 / P35 / P42 | 改剧本文字 → P05；要说话镜头与口型 → P35；已在剪辑台上接话 → P42 |

## 去重与合并记录

| 类型 | 说明 | 影响条数 |
| :--- | :--- | :--- |
| 同源双载体 | 每个子目录内 `提示词.txt` 与 `references/prompt-templates.md` 承载同一批 10 条（仅代码块围栏与空行差异，正文逐句一致），按 1 条计 | 5 目录 × 10 = 50 条冗余并入 |
| 全量合集 | 根目录 `50条可复制提示词.txt` 与五个 `prompt-templates.md` 同源，作为交叉校验来源，不重复计数 | 50 条冗余并入 |
| 子Bot 合并 | 原 `03 分镜与镜头设计` 与 `04 图片与视频提示词` 合并为 `sub-visual`，条目本身未合并 | 20 条同归一个子Bot |
| 内容近似但保留独立 | P27/P36/P43（独白三阶段）、P37/P44（音效生成 vs 音效表）、五处「检查」（P01/P10/P20/P30/P40/P49）——产物与阶段不同，**不合并**，靠上面冲突消解表分流 | 0 条合并 |

## 计数核对

- 唯一提示词：**50 条**（S 10 ＋ A 10 ＋ C 10 ＋ P 10 ＋ E 10）
- `sub-script` 10 条｜`sub-assets` 10 条｜`sub-visual` 20 条｜`sub-edit` 10 条 —— 合计 50 条
- 原始载体出现次数：50（`prompt-templates.md`）＋ 50（`提示词.txt`）＋ 50（`50条可复制提示词.txt`）＝ 150 次 → 去重后 50 条，合并冗余 100 次
