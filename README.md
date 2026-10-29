# 宣传片工作流工具包

**把题目或脚本交给 AI，用自己的素材，逐步做出能审看、能修改的视频和工程。**

这套工具把写稿、分镜、找素材、配音配乐、剪辑、验收和局部修改串在一起，适用于产品宣传片、品牌短片及录屏讲解。既可以从新题目开始，也可以保持已有定稿制作。

当前为 **v0.7.2 GitHub 测试预览版**。它是 AI 技能与命令工具包，需要支持 Skill 的 AI 工具、运行环境和使用者自己的素材／服务账号，不是双击就自动出好片的桌面软件。

[第一次使用](docs/首次使用.md) · [密钥与服务配置](docs/密钥与服务配置.md) · [项目介绍](docs/项目介绍.md)

## 能做什么

| 模块 | 实际用途 |
|---|---|
| 制作与导出 | 锁稿、事件分镜、素材复制与哈希、图片推拉／平移、已有视频剪辑、透明图层、多轨混音、MP4 导出 |
| 自建素材库 | 从空库开始，保存原件、查重分类、记录分析版本、文字检索、核对实际文件与备份数据库 |
| 参考拆解与产品片段卡 | 切镜候选、关键帧、页面与动作记录、分析缓存、按用途查找并引用；云分析需要自己的服务 |
| 动效库 | 363 条通用代码配方／样式，支持检索、导出、采用记录；21 种样式需另备媒体或布局 |
| 配音与配乐 | 中文豆包、英文 Google 接入；Google 生成音乐；自己的曲库选曲，保存请求、缓存与费用记录 |
| 审片和局改 | 视频打标插件、批准／拒收账本、快照回退、未标镜头和音轨对比 |
| 宣传片避雷 | 24 项通用规则与本片检查表，分镜前、负面反馈后、交付前读取并记录实际发现 |

363 条动效来自第三方通用代码与配方，保留各自出处及许可，不能当作全部自研。所有条目的动态效果尚未逐一验收。

## 从哪里开始

已经装有Git、Python3.10+、FFmpeg/ffprobe时，可直接复制以下下载和自检命令（macOS/Linux）：

```sh
git clone https://github.com/oumomomo/promo-video-workflow-kit.git
cd promo-video-workflow-kit
python3 video_setup.py doctor
```

Windows的Git命令相同，最后一行可用`py -3 video_setup.py doctor`。没有Git可下载发行ZIP，解压后在根目录运行自检。这是完整源码的获取和运行条件检查，不会自动安装系统运行时、注册所有AI宿主或配置云账号。

也可以把仓库链接连同这句话交给能读写本地文件和运行命令的AI工具：

> 请帮我安装并检查这个宣传片工具包：https://github.com/oumomomo/promo-video-workflow-kit 。读取README和首次使用指南，下载完整目录，先检查Python和FFmpeg；只补本次所需依赖。安装阶段不调用付费服务、不要求我先填所有Key。完成后告诉我该打开哪个目录、怎样用自己的素材做第一条片。需要服务密钥时由我在自己的环境中填写。

1. 下载并解压[发行包](https://github.com/oumomomo/promo-video-workflow-kit/releases/tag/v0.7.2)或本仓库，安装 **Python 3.10+、FFmpeg／ffprobe（含 libx264）**。Node 和额外 Python 依赖按所选模块说明安装。
2. 将需要的技能整个文件夹安装到 AI 工具支持的 Skill 目录。扩展工具和素材库依赖的同包技能需要保持同级；不要只复制 SKILL.md。
3. 给 AI 具体目标，提供自己的图片／录屏；或者使用 AI 当前实际可用的生成工具。图像、视频、声音模型的服务和额度不随包提供。
4. 先看分镜和风险镜头，再制作整片。检查实际导出的文件，审看后按明确范围修改。

也可以先在仓库根目录检查基础环境：

```sh
python3 video_setup.py doctor
```

这条命令分别报告基础制作与可选模块的依赖；默认只以基础制作判定退出状态。不读密钥或ADC、不请求云服务，不会自动生成视频。首次用自己的素材剪辑可以不配置任何包内服务Key。制作入口可以独立使用，不需要作者的数据库或其他私人项目。

### 可直接交给 AI 的任务

> 使用 video-making-kit，为我的产品制作一条 20 秒横屏宣传片。先读取宣传片避雷清单，再根据我提供的真实素材确定视觉方向和分镜。不要凭空发明产品功能或界面；画面中的动作要与旁白一致。需要生成内容时使用我的服务账号，并记录实际调用和费用。交付 MP4、可继续编辑的工程、检查记录和实际可用的审片入口。技术通过不代表我认可效果。

[安装与制作](docs/安装与制作.md) · [建自己的素材库](docs/建立自己的素材库.md) · [命令与制作协议](skills/video-making-kit/references/commands.md)

## 技能入口

- [video-making-kit](skills/video-making-kit/SKILL.md)：从题目／定稿到视频。
- [video-asset-library](skills/video-asset-library/SKILL.md)：自己的素材库。
- [video-reference-kit](skills/video-reference-kit/SKILL.md)：参考拆解、笔记与采用。
- [video-motion-kit](skills/video-motion-kit/SKILL.md)：动效配方与代码。
- [video-production-tools](skills/video-production-tools/SKILL.md)：片段卡、自动分析、声音、账本、门禁和回退。
- [视频打标插件安装](docs/打标插件安装.md)：插件需安装依赖并接入宿主；文件在仓库里不代表宿主已启用。

## 宣传片避雷经验

[24 项避雷清单](skills/video-making-kit/references/promo-pitfalls.md)来自两轮实际制作复盘和持续维护经验，包含：

- 画面不能只抓旁白中的名词；静图推拉不能冒充揉面、点击或其他真实动作。
- 有真实产品原片就先查看，继承界面结构和行为；不同页面不能拼成不存在的功能因果。
- 鼠标与控件使用一致的坐标，点击后有响应；镜头不反复放大缩小。
- 颜色、居中和留白本身不是 AI 味；判断材料来源、对象关系和画面职责。
- 音乐保持乐句连续，音效对应动作；无削波和响度正常不能替代试听。
- 局部修改保护未标镜头；实际文件 SHA-256 用来定位版本，不能只看 latest／final 文件名。

用[本片检查表](templates/promo-review.md)记录适用项、问题、修改和复查范围。这些是 AI 的执行指引，不保证每次自动遵守，也不能替用户批准审美。

## 使用自己的服务

完整步骤见[密钥与服务配置](docs/密钥与服务配置.md)。中文配音用豆包语音Key；Google音乐可用Gemini Key；英文配音和云分析目前走Google Cloud ADC登录与自己的项目，不能用一个Gemini Key代替全部服务配置。

Google 音乐支持使用者自己的 API Key：

```sh
python3 video_tools.py music configure-key
python3 video_tools.py music generate --prompt-file music-prompt.txt --output-dir music --dry-run
python3 video_tools.py music generate --prompt-file music-prompt.txt --output-dir music
```

先写实际音乐提示，再 dry-run 核对请求。macOS 可通过不回显交互将 Key 存入自己的钥匙串；其他环境使用自己的受保护环境变量 `GEMINI_API_KEY` 或 `GOOGLE_API_KEY`。不要把真实 Key 放进聊天、脚本、提交文件或参数。

已有 Vertex ADC 账号可显式选择 `--auth adc --project-id <自己的项目>`。不会回退使用作者账号。配音、分析与音乐库接入见[生产工具命令](skills/video-production-tools/references/operations.md)。

## 实际验证了什么

[首次安装自检报告](docs/首次安装自检报告.md)记录实际场景、修复和未测范围。

- v0.7.2候选包重新解压，在新建虚拟环境安装公开依赖后，**49项自动测试通过**；基础制作另有不装扩展包的7项编解码测试通过。复用系统FFmpeg/Node，不冒充全新电脑。
- 基于前一版相同渲染／服务逻辑，使用全新图片、新豆包配音和新 Google Lyria 音乐制作过 12 秒短片：1920×1080、30fps，360 帧全量解码通过。
- Google 音乐实际调用使用 Vertex ADC，重复请求验证了缓存；**API Key 通道目前只有模拟接口测试通过**。英文配音与云端视频／声音分析不能据此视为已实调。
- 样片是静图推拉蒙太奇，暴露了动作表达与画面／旁白匹配问题，未获用户审美批准，不作为高质量作品或效率提升证明。

没有完成陌生电脑、新手独立安装、Windows／Linux 实机、全部动效视觉或全部云服务验收。测试不包含模型额度。

## 范围与限制

不含作者私人素材、参考原片、字体、音乐、历史分析语料、生产数据库、账号、密钥或用户反馈附件。已有统一素材库时沿用原库，不新建平行生产主库。

复杂人物动作、物理过程、3D 或精细界面交互需要其他工具先制作成视频，再进入剪辑。在线音乐发现、部分原片获取、完整工作台和云协作尚未接齐。[与完整工作流的差距](docs/与完整工作流的差距.md)有逐项说明。

[发行状态](RELEASE-STATUS.md) · [第三方来源与权属状态](THIRD_PARTY_NOTICES.md)

自有代码与文档按 [MIT License](LICENSE) 发布；第三方代码保留各自许可和归属，见第三方声明。许可不包含云服务额度或私人素材。
