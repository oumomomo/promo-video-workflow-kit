# 命令与笔记格式

需要 Python 3.10+、Node.js 18+、FFmpeg 和 ffprobe；Python 与 Node 代码只使用标准库。命令示例在仓库根目录执行；独立安装技能时用技能内 `scripts/video_ref.py` 替代根入口。

## 开始使用

```sh
python3 video_ref.py doctor
python3 video_ref.py init --library ./my-library
python3 video_ref.py --library ./my-library prepare --source ./reference.mp4 --title "按钮操作参考"
```

`init` 只用于没有统一库的新环境。存在统一配置时，省略 `--library` 使用原入口，且 `prepare` 用 `--out` 指定当前项目的持久参考目录；不会修改全局配置或另建主库。

`prepare` 默认仅处理不超过180秒的视频，最多提取80个切镜候选的首尾帧；按实际范围可用 `--max-seconds`、`--max-shots` 调整。`--threshold` 是场景变化阈值，不是对镜头准确率的承诺。视频和音轨均不上传，声音仅记录是否存在。

命中本工具此前保存的同内容有效证据时，返回原证据位置，即使这次另给了 `--out` 也不重新提取。证据损坏或版本不同会明确报错，不覆盖旧分析。其他生产者的分析可经 `get` 读取，但本版尚不能自动转换所有历史格式。

## 补观察笔记

下文 `ASSET_ID` 替换为 prepare 输出的实际资产ID。

```sh
python3 video_ref.py --library ./my-library notes template --id ASSET_ID --out ./notes.json
```

打开原片和关键帧，按实际检查结果填写：

| 字段 | 含义 |
|---|---|
| sourceSha256 | 模板自动绑定的原片身份，不自行换成其他文件 |
| summary | 它能帮助解决什么表达问题，用于后续正文检索 |
| inspection.method | `agent_visual_review` 或 `human_review`，对应实际执行方式 |
| inspection.scope | 实际看过的页面、时间段、是否连续播放和检查限制 |
| inspection.observer/date | 实际执行者与日期 |
| audio | 实际声音检查状态与观察；未听辨保持未知 |
| phases | 可引用片段：start/end 为原片秒数，observed 写观察，inherit/change/avoid 写继承、替换及排除 |

这些字段是检查记录和声明，程序不能证明填表者确实看过，也不因此改变产品真源、权利或人工批准状态。

填写后提交并检索：

```sh
python3 video_ref.py --library ./my-library notes submit --id ASSET_ID --file ./notes.json
python3 video_ref.py --library ./my-library search "点击 结果"
python3 video_ref.py --library ./my-library get ASSET_ID
```

多个搜索词按同时包含匹配，正文中的用途与片段文字参与检索。本版是文字检索，没有语义向量检索或效果排序承诺。笔记更新保存新版本，同内容重试复用原回执。

## 关联到已有制作项目

目标项目目录应已存在。先按该项目现有规则核对锁稿和分镜，再关联实际片段，例如：

```sh
python3 video_ref.py --library ./my-library bind --project ./my-video --shot S01 --id ASSET_ID --start 0 --end 1 --inherit "操作后展示结果" --change "使用本次内容" --avoid "不推断原片未证明的联动" --use reference
```

时间应由实际原片和笔记确定，本示例的0到1秒不是通用剪辑参数。引用必须落在已记录的观察片段中。程序保存 `workflow/reference-uses.json`，并向同一资料库提交项目采用记录；初始状态为计划，未授予产品功能认可或用户批准。

同一镜头相同引用可重试，不覆盖不同引用。若已有项目使用其他正式分镜schema，先由Agent读取并按项目规则映射，这个文件不自动改写正式分镜。

如计划直接剪入原片，需要 prepare 时的 `--rights owned|licensed --rights-evidence "实际权利依据"`，再使用 `--use media`。这只是必要记录，不替代权利核验。

## 导出

```sh
python3 video_ref.py --library ./my-library export --id ASSET_ID --out ./reference-export.json
```

输出资产标题、来源和本工具的当前正文，不带视频字节。正文可能含本地路径或项目内容，导出仅用于自己的项目迁移与检查；公开分享前仍须审查。原件与旧版本仍在资料库，未执行云端备份。
