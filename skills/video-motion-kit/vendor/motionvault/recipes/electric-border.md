# 电流边框卡

深色卡片边缘盘绕着一道电流：SVG 滤镜把描边扭曲成电弧，光段沿边框流动，悬停时辉光更亮。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/card/ElectricBorder.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：hover

## 原始实现提示词

Create a React component called ElectricBorder using React + Tailwind CSS + SVG filters. Render a dark card (288×176px, zinc-900, rounded-xl) on a zinc-950 backdrop with minimal white content (mono uppercase label, title, two-line muted description). Overlay an absolutely positioned SVG (viewBox matching the card, inset-0, pointer-events-none) containing three rects (2px inset, rx 12, fill none): a faint white/8 base outline, a crisp traveling arc (stroke zinc-200 #E4E4E7, strokeWidth 1.4, strokeLinecap round, pathLength 260, strokeDasharray "46 214"), and a blurred glow copy (stroke #F4F4F5, strokeWidth 3.5, 3px blur, same dash, opacity 0.55 → 1 on card hover via CSS transition). Wrap the arcs in a group with filter url(#eb-distort): feTurbulence (fractalNoise, numOctaves 2, seed 4, filter region −20%/140% so displacement is not clipped) whose baseFrequency is SMIL-animated between "0.012 0.05" and "0.02 0.085" over 5s, feeding an feDisplacementMap (scale 7) — the border warps like a live current. Animate stroke-dashoffset 0 → −260 in a 3.2s linear infinite CSS keyframes loop so the arc flows around the border; pause with animation-play-state when the card is off-screen (IntersectionObserver). Isolate the SVG in a memoized micro-component.
