# 来源、许可与第三方声明

## 自有部分

维护者于2026-10-29确认：本仓库自行开发的工作流、制作执行器、资产模块、分析与配音工具、生产记录工具及视频打标插件有权公开，按根目录 [MIT License](LICENSE) 发布。相关工具由既有生产环境提炼、适配为可移植实现；没有携带私人生产数据、媒体、账号或历史反馈。

MIT只覆盖有权授权的自有部分，不覆盖下列第三方代码、外部依赖或云服务。`SOURCE.json`中的原始哈希记录移植前快照，不是所有文件当前哈希；当前发行身份见`SOURCE-MANIFEST.json`。

## video-shots：Apache-2.0

`skills/video-reference-kit/vendor/video-shots/`来自已安装分析工具附带的video-shots代码，保留所附Apache-2.0 LICENSE、README、工具及报告资产，不含其示例视频或帧图。

README提及[eternityspring/shuohao-skills](https://github.com/eternityspring/shuohao-skills)作为方法参考；本次没有验证video-shots的直接公共仓库或精确提交，不将该链接冒充已核实的直接上游。它按原附许可保留，不改称本仓库原创或MIT代码。可通过Issue补充可核对的直接来源或归属信息。

## video-shotcraft：Apache-2.0

`skills/video-motion-kit/vendor/video-shotcraft/`来自[Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft)，摄取时本地干净HEAD为`d4915443232e89527fdc9d7e79f132ba411fc440`。保留原Apache-2.0 LICENSE（Copyright 2026 Wei Yihao）。选入配方及代码未改动，不含预览视频、截图、音频或字体。逐文件来源哈希见动效技能的`references/provenance.json`。

## MotionVault：MIT

`skills/video-motion-kit/vendor/motionvault/`的202条配方和React代码来自[xiyu519/MotionVault](https://github.com/xiyu519/MotionVault)。原摄取版本记录为`0a201da92e4b4fa7436b1c79c7f249bc66329644`，本次没有重新获取上游提交。保留其MIT LICENSE（Copyright 2026 MotionVault Contributors）；目录、配方及代码来源保留，不将其宣传为全部自研。

## 打标插件依赖

打标插件应用代码由维护者确认可按MIT发布。浏览器bundle使用的MCP相关依赖许可另见`plugins/codex-video-review/DEPENDENCY-NOTICES.md`；锁文件记录完整依赖身份，不捆绑node_modules。应用许可不重新授权其依赖。

## 外部运行时与服务

Python、FFmpeg、Node、Remotion、React、Framer Motion、GSAP、Three.js、numpy、websockets和certifi等按各自许可安装使用；本仓库不捆绑这些运行时或付费额度。第三方配方源码的许可不代表其运行时或所有商业使用都免费。

Google音乐/配音/分析、豆包配音及宿主图像/视频工具须使用自己的账号。服务和生成内容适用使用者的服务协议；本仓库源码许可不等于素材再分发、肖像、商标或音乐独占权证明。密钥只在运行时读取，不放在仓库或发行包内。

## 经验和测试

宣传片避雷清单来自维护中的通用制作经验与两轮复盘提炼，不含原始聊天、真实客户资料或历史媒体。自动测试使用临时合成输入；新题样片媒体和费用凭据留在测试环境，没有随源码公开。
