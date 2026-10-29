# 签名描绘

一段手写体的 “Motion” 签名逐笔描绘出自己，最后一条下划线潇洒收尾，每 4 秒自动重播。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/svg/DrawSignaturePreview.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React component called DrawSignature using React + Tailwind CSS + Framer Motion. It renders an SVG (viewBox 400x130) containing a hand-crafted cursive 'Motion' written as one flowing connected path of smooth cubic curves on a baseline near y=88. The main word draws itself with a motion.path animating pathLength 0 to 1 over 2.2s with ease-in-out, stroke #09090B (zinc-950), strokeWidth 3, round line caps and joins, no fill. Two tiny detail strokes (a t-cross and an i-dot) draw near the end with short 0.25s pathLength tweens around 1.75s delay. Then an underline flourish path (a long sweeping curve from x=42 to x=356 near y=100 with an upward hook at the end) swishes in with pathLength 0 to 1 over 0.4s at 2.25s delay. The whole sequence replays automatically every ~4.2s by incrementing a cycle counter in state and keying the svg on it so all strokes remount; clean up the interval on unmount. Center the svg in the container on a light background, animate pathLength only.
