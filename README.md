# 宣传片工作流工具包

**把题目或脚本交给 AI，用自己的素材，逐步做出能审看、能修改的视频和工程。**

这套工具把写稿、分镜、找素材、配音配乐、剪辑、验收和局部修改串在一起，适用于产品宣传片、品牌短片及录屏讲解。既可以从新题目开始，也可以保持已有定稿制作。

当前为 **v0.7.3 GitHub 测试预览版**。它是 AI 技能与命令工具包，需要支持 Skill 的 AI 工具、运行环境和使用者自己的素材／服务账号，不是双击就自动出好片的桌面软件。

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

**不用先弄懂Git、Python或FFmpeg。把仓库链接交给能操作本地文件和终端的AI，让它检查并准备本次需要的环境。**

可以直接复制：

> 请帮我接入这个宣传片工具包：https://github.com/oumomomo/promo-video-workflow-kit 。先读README、首次使用和环境准备指引，判断我的系统与已有工具，下载完整目录；缺什么就在安装授权范围内补什么。没有Git就下载ZIP，Python缺失就先准备Python，再运行video_setup.py doctor。优先使用项目/用户级环境。需要管理员操作或登录时只告诉我具体一步；安装阶段不调用付费生成服务，不要求我提前填写所有Key。完成后告诉我怎样用自己的素材做第一条片。

**给接手的AI：** 先读[环境准备指引](skills/video-making-kit/references/environment-setup.md)，再按[首次使用](docs/首次使用.md)执行。先判断系统和实际工具，再安装缺项；不要把依赖名词清单当作用户必须自己完成的作业。宿主没有本地执行权限时，明确说明限制并提供最少人工步骤。

当前没有把各系统的Python/FFmpeg二进制捆进仓库，也没有通用的一键安装器。Git只用于克隆/更新，下载ZIP可省掉；Python3.10+和FFmpeg/ffprobe是基础制作实际需要的运行时。图像生成与AI宿主按其实际配置使用；服务密钥在需要时再由用户填写。

### 也可手动下载与检查

已安装Git、Python3.10+和FFmpeg时，macOS/Linux可执行：

```sh
git clone https://github.com/oumomomo/promo-video-workflow-kit.git
cd promo-video-workflow-kit
python3 video_setup.py doctor
```

Windows最后一行可用`py -3 video_setup.py doctor`。没有Git则下载[发行ZIP](https://github.com/oumomomo/promo-video-workflow-kit/releases/tag/v0.7.3)，解压后运行自检。只复制SKILL.md会丢失脚本、模板或插件，保留完整目录。额外依赖和打标接入由AI按本次模块处理，详见首次使用指南。

自检分别报告基础制作与可选模块依赖；默认只以基础制作判定退出状态。不读密钥/ADC、不请求云服务，不会自动生成视频。已安装不等于已注册宿主工具，参数预演也不等于服务权限已验证。

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
