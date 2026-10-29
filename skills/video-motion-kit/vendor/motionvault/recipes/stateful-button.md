# 状态变迁按钮

点击后 '部署' 变为旋转 loading 环，再变为打勾 '完成'，按钮宽度随内容弹性伸缩，随后自动复位。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/button/StatefulButton.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：click

## 原始实现提示词

Create a React component called StatefulButton using React + Tailwind CSS + Framer Motion (Aceternity Stateful Button). A dark zinc-950 pill (h-11, min-w 104px, rounded-lg, white text). On click run a phase machine idle → loading → done → idle: idle shows the label '部署'; loading (1.2s) swaps to an inline spinning ring (h-4 w-4, border-2 border-white/25 border-t-white, rotate 360 on a 0.8s linear infinite loop); done shows a drawn check (SVG path M 3 8.5 L 6.5 12 L 13 4.5 animated with pathLength 0→1 over 0.5s) plus '完成' for 1.5s, then resets. Swap phases with AnimatePresence mode popLayout (initial/exit opacity + y ±8 / scale 0.6, 0.18s) and put layout on the button with a spring (stiffness 500, damping 32) so its width stretches elastically to fit each content state. Disable the button while busy; store timeouts in a ref array and clear them all on unmount.
