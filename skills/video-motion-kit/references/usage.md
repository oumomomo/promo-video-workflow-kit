# 使用与适配

`CLI` 表示本技能的 `scripts/motion.py` 实际路径，或源码包根目录的 `video_motion.py`。

```sh
python3 CLI stats
python3 CLI audit
python3 CLI search '数字' --runtime remotion --no-media --limit 6
python3 CLI resolve odometer-digit-roll
python3 CLI export odometer-digit-roll --out ./motion-source
python3 CLI scaffold slow-push-in --demo SlowPushIn.tsx --frames 150 --out ./motion-shot
python3 CLI record slow-push-in --project ./my-video --shot S03 --mode remix --reason '用推进把注意力集中到本片对象' --change '替换示范数字、配色和对象' --avoid '不把示例性能声明带入本片'
```

`search` 是文字与小型别名表检索，多个词按命中数排序，不是向量语义搜索。`resolve` 回读完整配方、准确Demo路径、哈希、NPM导入项和缺失媒体；不会播放动态预览。`audit` 核对来源文件完整性与无媒体白名单，不能证明全部组件可运行或美学合格。

## 导出与运行

`export` 要求空目录，复制条目对应配方、代码闭包与许可证，生成 `MOTION-SOURCE.json`。不复制项目使用历史或主库数据。文件可能包括同卡多个Demo；正式采用须读取并选择准确实现。上游代码未改，部分保留示例文案与系统字体栈，需要按本项目适配，不表示品牌、性能或字体效果已验证。

`scaffold` 只接受无媒体缺口的Remotion条目。多实现条目须用 `--demo` 指定准确文件；不能确定组件导出时用 `--component`。代码需要props时仍须阅读源码并补 `defaultProps`。模板30fps／1920×1080，默认150帧只是试验起点，时长按配方与实际镜头调整。

在生成的工程中：

```sh
npm install
npm run still
npm run render
```

工程内的React／Remotion版本明确固定，NPM依赖和浏览器由环境安装，不在压缩包里。若渲染工具下载浏览器失败，先修复该依赖问题，不把源码导出说成视频完成。Remotion等运行时的许可独立于配方代码的许可证。

网络限制导致默认无头浏览器下载失败时，可以使用已安装的Chrome／Chromium可执行文件。例如 `npm run still -- --frame=15 --browser-executable='<本机Chrome可执行文件>'`，路径由当前环境确认，不读取个人浏览器资料。本轮两个单镜工程使用新装NPM依赖与系统Chrome，分别渲染了第15和105帧；没有将浏览器或渲染结果打进包，也不据此称为完整动态验收。

输出 `out/motion-candidate.mp4` 是单镜示范／候选。替换示例对象、品牌与文案后再纳入正式视频。任何可供用户审看的单镜视频，也应按宿主能力提供实际文件对应的审片入口。

## 不带旧媒体的处理

截图、视频、音频、字体、预览MP4／GIF、布局测量JSON全部不带。某些Demo还保留导入旧纹理的代码，`missingMedia` 显式记录这个依赖。需要这些镜头时先 `export`，由当前用户提供或新生成素材，再修改源码引用与布局；`scaffold` 在此之前拒绝创建可直接渲染工程，避免暗中使用本机旧图。

代码生成的SVG路径、几何图形、色块和粒子属于动画程序，不是随包携带的旧图片。通用配方文字属于动效知识；本工作区的产品拉片报告、参考原片和历史分析语料未打包。

## 网页效果怎样用于视频

202条MotionVault效果包含React、CSS/Tailwind、Framer Motion、Three.js或GSAP实现。随包代码包含所需本地helper；NPM依赖须按 `npmImports` 和上游版本另装。`@/hooks`、`@/lib` 指向导出目录 `vendor/motionvault/src/`，配置项目别名，不指向原电脑。

把悬停、点击、滚动或实时循环转换为本片的事件帧：

1. 从源码确认真正变化的量，例如卡片宽度、字距、粒子位置或相机角度。
2. 确定起态、动作、落定和停留时间，不让系统时钟决定视频进度。
3. 在Remotion中用 `useCurrentFrame` 和确定性插值计算每帧；随机数固定种子。Three.js的时间与相机同样绑定帧。
4. 原网页组件可以作为算法／结构参考；实时预览可动不等于视频随机定位正确。检查起、中、末及动作转折，再正常速度观看。

这些效果不宣称已全部转换成Remotion。本轮仅完整打包可检索配方、代码与本地依赖，并验证相应范围；不会把202条网页源码算成202条现成可渲染视频镜头。
