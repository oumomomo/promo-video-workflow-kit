# 下载变形

点击后按钮原地变形成进度条——填充条先快后慢地爬满，百分比同步跳动；完成后翻转为绿色对勾，随后悄悄复位。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/button/DownloadButton.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：click

## 原始实现提示词

Create a React DownloadButton component using React + Tailwind CSS + Framer Motion. A fixed-width black pill (w-44 h-11, rounded-full, bg-zinc-950, white text '下载文件' with a Download icon from lucide-react). It is a click-driven state machine (not re-clickable while running): (1) on click the label cross-fades out and the pill morphs into a progress track — its width stays fixed, the background transitions to zinc-200 over 300ms — while a dark fill bar grows 0 → 100% over 2s with a fast-start/slow-end ease (cubic-bezier(0.16,1,0.3,1)); drive progress with framer-motion's animate() on a MotionValue, render the fill with transform scaleX (origin-left) and show a live mono percentage counter (motion value as child, white text with mix-blend-difference so it reads on both track and fill). (2) At 100% the fill fades away as the pill flips to green #16A34A with a Check icon + '已完成' popping in (spring scale 0.6 → 1). (3) After 1.6s it quietly fades back to idle. Swap content with AnimatePresence mode="wait"; transform/opacity only. Center on a light preview.
