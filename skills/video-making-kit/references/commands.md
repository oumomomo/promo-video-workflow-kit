# 可执行协议

以下 `CLI` 指安装后 `video-making-kit/scripts/video_make.py` 的实际位置，或源码包根目录的 `video_make.py`。命令没有模型调用，不会自己写文案或生成产品照片，宿主AI按SKILL执行这些工作。

```sh
python3 CLI doctor
python3 CLI init --project ./my-video --brief '为虚构品牌做一条15秒新品短片'
python3 CLI lock-script --project ./my-video --file ./script.txt --origin agent_authored_for_requested_task
python3 CLI add-asset --project ./my-video --id hero --file ./hero.png --kind image --origin generated --source '实际工具、提示词记录位置' --rights generated --basis '本次生成；公开使用条件另核对'
python3 CLI validate --project ./my-video
python3 CLI render --project ./my-video --out out/candidate-r01.mp4
python3 CLI check --project ./my-video --file out/candidate-r01.mp4
```

`doctor` 的 ready 只代表CLI运行条件。若要生成画面／口播，另核对宿主工具；缺工具不是让用户反复安装这个源码包。FFmpeg及Python由使用者安装，不捆绑二进制。

`init` 要求空目录。先修改 `workflow/brief.json` 里的具体要求，再锁稿，锁稿会更新需求哈希。现有锁稿不被覆盖；改稿另保留项目版本。编辑分镜只写 `workflow/plan.json`。素材用 `add-asset` 复制到 `assets/`，清单在 `workflow/assets.json`，全部执行路径相对于项目根目录。不要把整机资产导入此清单。

## 分镜JSON

示意协议，素材和数值须换成本次实际内容。空项目不会生成这些占位镜头。

```json
{
  "schemaVersion": 1,
  "briefSha256": "由lock-script填写",
  "scriptSha256": "由lock-script填写",
  "canvas": {"width": 1920, "height": 1080, "fps": 30},
  "visualDirection": "本次实际方向、对象和质感",
  "paletteBasis": "本次实际配色依据",
  "shots": [{
    "id": "S01", "duration": 3,
    "scriptRange": [0, 12],
    "asset": "hero",
    "event": "起态→事件→结果；注明静图推近或实际动作",
    "focus": "一个首要阅读对象",
    "connection": "与下一镜的构图或语义衔接",
    "acceptance": "可观察的通过条件",
    "zoom": [1, 1.06],
    "pan": [[0.5, 0.5], [0.6, 0.5]],
    "layers": [{"asset": "transparent-title", "start": 0.5, "end": 3, "fadeIn": 0.2, "fadeOut": 0}]
  }],
  "audio": {"mode": "silent", "reason": "本次明确的静音原因", "tracks": []}
}
```

`scriptRange` 是锁定文件UTF-8文本解码后的Python字符下标 `[start,end)`，不是字节、帧或词时码。每个非空白字符至少被一镜覆盖；此检查不证明语义正确或实际字幕完整。总时长以镜头时长之和为准；每镜对齐整数帧，画幅须为偶数整数。

静图先等比填满并中心裁切，再推拉；zoom是裁切后画面的放大倍数1–4。pan是放大后可移动范围内的归一化位置，0为左／上、1为右／下，0.5为中间。它不是自动跟踪，也不能移动原图外的内容。用首中尾帧检查是否裁掉主体。叠层会缩放至整幅画布，应预先做成与画幅同尺寸的透明PNG；文字、标注和绘图由Agent用可用工具制作，不能依赖宿主机器字体路径。

视频素材不接受zoom/pan，以 `in` 秒数为入点，取该镜时长，等比填满并中心裁切。复杂运镜、抠像、3D、人物动作等先做成视频再注册；不要谎称内置通用剪辑器能自动实现。每镜硬切，不自动叠加溶解；有意转场须先制作在镜头素材中。该执行器不支持速度重定时与自动节拍检测。

叠层区间相对本镜，`[start,end)`；fadeIn/fadeOut各不超过区间一半。使用多层图可承接品牌字卡，但执行器不会判断必要性。

## 多轨混音

```json
{
  "mode": "mix",
  "reason": "口播讲述、音乐连贯承托；不循环",
  "tracks": [
    {"asset": "narration", "role": "voice", "at": 0, "in": 0, "duration": 15, "gainDb": 0, "fadeIn": 0, "fadeOut": 0},
    {"asset": "music", "role": "music", "at": 0, "in": 8, "duration": 15, "gainDb": -15, "fadeIn": 0.4, "fadeOut": 1.2}
  ]
}
```

时间须在原件与成片内。增益、淡入淡出和落点显式指定；混音不自动归一化、不自动压口播、不靠限幅掩盖削波。`check` 的接近满刻度提醒须回听或修正，不代表全频听感通过。原视频声音默认不带入，若采用须把该视频明确列为声音轨。

## 输出和搬家

`render` 不覆盖已有MP4；保存同名 `.render.json`（输入身份、命令与候选状态）。`check` 保存 `checks/*-technical.json`、音量信号记录和逐镜首中尾抽帧。命令记录可能保留执行时的临时路径用于追溯；重跑只读取项目相对路径，不读取这些回执里的旧路径。

工程迁移需整个项目目录，包括 assets、锁定脚本和workflow；在新目录用新的输出名重跑validate/render/check才可称为验证过恢复。迁移源码包不自动修复其他素材库路径。候选不写统一库、不发布。
