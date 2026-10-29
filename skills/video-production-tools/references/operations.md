# 可执行入口

从包根目录执行。--library传使用者自己已建的库；已有统一配置时省略。不得为测试在既有工作区创建第二套主库。

## 产品片段卡

```sh
python3 video_tools.py --library ./my-library cards intake --project ./film --file ./recording.mp4 --role product_ui_original --product-name "实际产品" --provenance "实际来源依据" --inspection-scope "实际观看范围"
python3 video_tools.py --library ./my-library cards publish --cards ./实际返回路径/segments.json
python3 video_tools.py --library ./my-library cards find "页面 动作"
```

intake返回source-index与segments路径。每段填写id/title/observed/keywords/status/reviewScope；视频有startSeconds/endSeconds/keyframesSeconds，图片有imageRegion。candidate不发布；structure_reviewed只支持静态结构；action_reviewed必须记录连续观看范围及action/beforeState/afterState，不能用抽帧核实点击结果。这些为实际检查者的声明，不是工具亲自看过。发布保留文档历史，检索最新卡片。

## 自动视频/声音分析与复核

依赖Python3.10+、FFmpeg/ffprobe、numpy；pip安装见requirements.txt。先用本地原件：

```sh
python3 video_tools.py --library ./my-library analyze --source ./recording.mp4 --out ./analysis --cloud none
```

本地输出cuts.json、analysis.json、precision.json、sound-reuse.json、evidence.html与HANDOFF.md，原始帧PTS与混音瞬态只作候选证据。cloud none的语义状态保持incomplete/needs_cloud_authorization，退出1是明确未完成语义分析，不是声称已精拉；文件仍可复核。

Google Vertex分析用GOOGLE_CLOUD_PROJECT指定自己的项目，VIDEO_ANALYSIS_MODEL可覆盖模型，默认保留迁移源的gemini-2.5-flash；不声称它是最新或保证仍对所有账号可用。用gcloud ADC配置使用者自己的身份。grant.json必须记录真实已有授权，结构为{"mode":"video","endpoint":"自己的实际Vertex端点","sourceHashes":["原件SHA256"]}，服务、模式与文件均匹配才可发送。`--cloud video --authorization ./grant.json`会上传视频分段并可能收费；audio只上传声音。不要为运行方便捏造授权。`--submit`把结果交给同一素材库。

保存分段模型返回和重试，成功候选按哈希/模式缓存。模型/服务配置属于缓存身份的一部分；错误不冒充完成。云端API尚未在本次发行验证中实调。没有Jev私有环境依赖，也不自动下载原片；先用宿主获准的来源取得文件。音效替代适配本轮不接作者私有声音库，未知保持空候选。

## 配音与费用

```sh
python3 video_tools.py voice select --text-file ./film/workflow/script.locked.txt --output-dir ./film/voice
python3 video_tools.py voice synthesize --text-file ./film/workflow/script.locked.txt --output-dir ./film/voice --dry-run
```

核对后，在用户已有授权覆盖下移除--dry-run生成。中文使用豆包公版音色；配置自己的DOUBAO_TTS_API_KEY环境变量，或显式执行voice configure-doubao交互写入当前使用者macOS钥匙串。不要把密钥写进项目或配置样例。英文需要自己的Google项目（--project-id或GOOGLE_CLOUD_PROJECT）、gcloud ADC。不能用作者项目作为默认值。

默认连续一条旁白，可用--mode shots按实际分镜配音；不克隆来源音色。五种通用声音风格来自原工作流方法，未携带私人系列/逐镜声音参数。缓存保存音频及SHA回执，缺失或不符会失败；--force仅在用户要求重新生成时用。输出voiceover-manifest.json；validate检查实际音频，不等于试听或逐字ASR通过。

```sh
python3 video_tools.py music cost --manifest ./film/voice/voiceover-manifest.json --prices ./my-prices.json
```

价格文件可提供各provider的perSecond预算费率与currency/source/verifiedAt，例如{"doubao":{"perSecond":null,"currency":"CNY","source":"使用者核验的官方价格页","verifiedAt":null}}。这只是按实际新增秒数的预算换算，不冒充供应商计费公式；为空返回未知，缓存请求返回新增费用0。实际豆包/Google服务若按字符/token计费，应以官方当期规则和账单核算。包不带过期固定价格表，不含额度。analysis原始响应中的usageMetadata、重试记录也须纳入新增调用统计，不能只算成功次数。

## 自动选音乐并接入剪辑

```sh
python3 video_tools.py --library ./my-library music add --file ./my-track.mp3 --title "自己的曲目" --license-file ./actual-rights.txt --rights licensed --source-url https://实际来源页 --tags calm
python3 video_tools.py --library ./my-library music plan --query "calm" --seconds 18 --out ./film/music-selection.json
python3 video_tools.py music apply --project ./film --selection ./film/music-selection.json
python3 video_make.py validate --project ./film
```

接着按原制作入口render/check并实际听辨。仅从使用者库中足长、原件及许可证据哈希通过的owned/licensed曲目选择；按文字标签匹配，0分仅可标为可用保底，不能称为最佳风格。没有可用曲目时明确缺项，不伪造我们的保底音频，不自动抓取受限站点，不自动循环/变速。固定BGM增益及首尾淡入淡出，保留旁白轨；同片已有BGM则拒绝叠加。source URL及许可为使用者声明，自动校验文件不代替实际核权。在线发现/生成音乐服务仍由宿主选择与配置；此自动配乐执行器从自己的本地库选曲。

## 生产账本、局改保护、回退

```sh
python3 video_tools.py ledger --project ./film init
python3 video_tools.py ledger --project ./film snapshot
python3 video_tools.py ledger --project ./film decision --file out/r01.mp4 --status rejected --by "实际反馈人" --evidence feedback/request.txt --scope "实际范围" --reason "实际反馈"
python3 video_tools.py ledger --project ./film protect --shots S02 --baseline out/r01.mp4 --evidence feedback/request.txt
python3 video_tools.py ledger --project ./film verify --candidate out/r02.mp4
python3 video_tools.py ledger --project ./film rollback --snapshot 实际快照ID
```

feedback/request.txt须保存实际用户意见，不写成Agent伪造批准。verify严格比较未标镜头解码帧和音轨，编码导致像素变化也会失败，需要核对原始分段与合成策略，不能擅自忽略。回退只恢复快照包含的流程文件，不重写视频、不删除素材；回退前当前状态另存。ledger记录不投影到Univer或代替其远程worktree。另带archive-audit原生产账本的项目本地init/audit/validate，用于已有production-archive schema；二者各有职责，生产决策/快照以ledger为准，archive.json是可选详细交付账本，不自动复制数据库或批准。

## 视觉合同和原片证据

```sh
python3 video_tools.py contract --project ./film init
python3 video_tools.py contract --project ./film check
python3 video_tools.py evidence ./film/workflow/source-evidence/shot-evidence.json --workspace-root . --recreation-stage preproduction
python3 video_tools.py evidence ./film/workflow/source-evidence/shot-evidence.json --workspace-root . --recreation-stage delivery
```

contract起草每镜来源与职责，check检查覆盖。evidence按本工作流原协议逐镜绑定原片、观察范围、允许替换和禁用内容，加入sourceRecreation的原帧路径/哈希/recreate/adaptContent；交付时另有candidateFramePath/candidateFrameSha256/comparisonStatus/comparisonNotes/reviewedBy。正式真实功能主张另用--require-ready。模板和检查不替代实际查看，详见review-method.md。

## Google生成音乐（v0.7）

新用户可填写自己的Google AI Studio API Key。包不保存Key明文或包含作者账号：

```sh
python3 video_tools.py music configure-key
python3 video_tools.py music generate --prompt-file ./film/music-prompt.txt --output-dir ./film/music --dry-run
python3 video_tools.py music generate --prompt-file ./film/music-prompt.txt --output-dir ./film/music
```

configure-key在macOS用不回显交互写当前使用者钥匙串。也可在自己的受保护环境设置GEMINI_API_KEY或GOOGLE_API_KEY；不要在聊天、脚本参数、提交文件或.env样例里填写真实Key。默认lyria-3-clip-preview，30秒音乐；--model可显式选择支持的模型。纯音乐提示写Instrumental only, no vocals，并给出器乐、节奏、氛围和结束方式。使用者须有相应API权限与额度。

Gemini API Key走generateContent；原工作流的Vertex账号认证保留为显式--auth adc --project-id <自己的项目>，走interactions。两条路径不互相降级，不共用作者项目。操作会向Google发送当前文本提示，不上传原片；先dry-run检查。根据2026-10-29官方价格，clip为每首预计US$0.04，Pro/3.5预计US$0.08；价格与模型可用性须随官方更新，manifest为估算而非账单。

请求、费用、音频SHA、实际时长、完整解码与状态保存在generation.json；密钥和请求头不保存。相同请求成功后复用缓存，校验失败不自动重生；已发出但超时/失败的请求停止重试，防止重复费用。检查原回执，确认后为新的明确请求另建目录。不要通过换目录无脑重试未知结果。

生成后把generation-evidence.txt作为生成身份和条款记录接入自己的曲库（生成身份不等于独占权利或发布批准）：

```sh
python3 video_tools.py --library ./my-library music add --file ./film/music/bgm-generated.mp3 --title "本次新生成音乐" --license-file ./film/music/generation-evidence.txt --rights generated --source-url https://ai.google.dev/gemini-api/terms --tags calm
```

再用plan/apply与video_make渲染。可以只裁取需要的连续区间，不自动循环、变速或拼重复开头。实际听辨音乐性与混音，文件/音量合格不代表听感通过。

官方接口：https://ai.google.dev/gemini-api/docs/generate-content/music-generation
官方价格：https://ai.google.dev/gemini-api/docs/pricing
Vertex接口：https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/music/generate-music
