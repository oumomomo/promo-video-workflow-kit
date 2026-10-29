# 建立自己的素材库

这套方法把“文件放在哪”和“AI怎样找到、理解、采用它”一起记录。原视频/图片/声音在磁盘，SQLite保存身份、路径、分类、来源、分析版本与项目引用。只堆文件夹不能代替可检索的分析，只有数据库也不能播放丢失的媒体。

本包不带作者的数据库、原片、分析积累或账号。初始化会在使用者自己的目录生成空assets.sqlite与config.json；第一次入库后生成objects。数据库结构由video-reference-kit现有引擎创建，不另建主库。两个技能文件夹须同级一起安装。

## 1. 选定一个库

全新环境运行（路径可按自己的磁盘安排）：

```sh
python3 video_library.py --library ./my-library init
python3 video_library.py --library ./my-library stats
```

只用于没有既有统一入口的新环境，拒绝覆盖非空目录。已有统一素材库配置或工作区要求时不执行init，也不新建旁路库，省略--library沿用已有entry.py。已有入口失效应修原配置，不能通过屏蔽配置强建第二套。本工作区有现成主库，因此本轮只在独立临时测试环境验证，未执行真实建库/入库。

## 2. 收到材料先判角色

| 材料 | 如何处理 |
|---|---|
| 外部宣传片/表达参考 | reference，按实际用途分类；没有授权可以研究，不因此能剪进自己的片 |
| 真实产品原始截图/录屏 | product-original，记录产品名、来源身份和实际观看范围；未观察的动作保持未知 |
| 审片圈注、候选截图 | feedback，仅作反馈；默认不参与普通素材检索 |
| 聊天/报错/沟通截图 | context或unverified，不能当产品原片 |
| 自己的候选、样片、验证短样 | 只留项目，不入库 |
| 用户明确指定归档的成片 | final + user_archived_video，保留具体归档指令依据，普通文件名final不构成批准 |

kind是文件用途类型，如image、reference_video、audio、music_track、sound_effect、font、motion_capability、method、analysis_document；category是内容用途，如产品宣传片、界面操作、数据变化、纸张音效。来源平台与内容用途分开。标签和用途要写实际可检索内容，不能仅填“好看”“高级”。

## 3. 哈希查重，保存原件副本

```sh
python3 video_library.py --library ./my-library lookup --file ./input/reference.mp4
python3 video_library.py --library ./my-library ingest --file ./input/reference.mp4 --title "本次参考" --kind reference_video --category "产品宣传片" --role reference --tags "对象接力" "展开" --use "对象如何从一个场景传到另一个场景" --rights unknown
```

新用户便携库会复制到objects/<SHA-256>/source.<扩展名>并校验，原文件不删除。同内容复用身份；同内容已有不同证据角色则要求复核，不静默把反馈提升为产品原片。统一库模式依既有入口登记用户提供的持久文件，不另做隐式媒体搬家。

产品原片须额外提交--product-name、--provenance、--inspection。自有/已授权需--rights owned或licensed及--rights-basis。权利依据写入版本化catalog-notes，get会返回当前记录；它是声明，不是自动法律核验，unknown不可被描述为可自由剪入素材。标签、用途和分析正文参与文字检索，尚无向量语义搜索。

## 4. 分析后保存新版本

先实际查看/听辨，写清能借鉴什么、对应时间段、未检查什么；将UTF-8文本通过同一ingest的--analysis ./analysis.md登记。程序保存新结果版本，相同正文重试复用回执；不会把模型候选升级为人类审美通过。

参考视频需要逐镜、动作阶段和声音观察时，用已有video_ref.py，不另建库：

```sh
python3 video_ref.py --library ./my-library prepare --source ./input/reference.mp4 --title "本次参考"
python3 video_ref.py --library ./my-library notes template --id ASSET_ID --out ./notes.json
```

ASSET_ID用实际返回值替换。查看原片并填notes.json，再notes submit。prepare只生成机械证据；不是AI云端精拉或声音听辨。详细字段见video-reference-kit的references/commands.md。当前通用登记先保存文件身份、再提交分析笔记，不是一笔总事务；后一步失败时重跑同一命令，不能宣称笔记已提交或删除原件。

## 5. 下一次制作先找再看

```sh
python3 video_library.py --library ./my-library search "对象 接力"
python3 video_library.py --library ./my-library get ASSET_ID
```

search先得到候选，get回读来源、当前catalogNotes和实际哈希通过的verifiedLocalFiles。根据原片/图片/音频实际内容选择。产品真源可用--scope product-ui收窄，但登记字段齐全不代表动作全部验证；仍须查看对应页面/时间段。普通检索排除feedback/context。

逐镜采用参考用同库video_ref.py bind，记录项目、镜头、原片时间段、继承/替换/排除；直接剪入原片需核实权限。动态配方和代码可以入库，但代码登记不等于已可执行或通过视觉验收。包内363条通用动效发行目录继续通过video_motion.py读取，不在初始化时复制到新库，也不是第二个生产主库。

## 6. 备份与恢复

```sh
python3 video_library.py --library ./my-library backup --out ./backup/assets-20261029.sqlite
```

此命令使用SQLite backup并做完整性检查，拒绝覆盖，但只备份数据库。完整备份还需复制config.json、objects、references等库文件及实际项目采用工程，回读校验各原件哈希。数据库保存路径不是媒体本身。该命令没有上传夸克，不得说“云备份已校验”。

便携get会优先核对当前库内按哈希存放的原件，因此这部分库移动后仍能找到对象；其他旧记录、参考分析目录和项目采用可能有历史绝对路径，需要逐项恢复/核验，不能声称完整工程自动迁移。生产统一库的云回执、多人共享、产品片段卡、Univer界面和全部生产档案未由本入口实现。
