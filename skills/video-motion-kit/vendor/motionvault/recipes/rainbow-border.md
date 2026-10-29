# 彩虹边框

白底按钮外圈是一环缓缓旋转的低饱和彩虹，模糊的副本晕开成柔光——克制而不艳俗。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/button/RainbowBorder.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React component called RainbowBorder using React + Tailwind CSS + scoped CSS keyframes. A white pill button (bg-white, zinc-900 text) sits inside a relative wrapper padded by 2px so the border ring shows through. The ring is a slowly rotating pastel conic-gradient — conic-gradient(from 0deg, #F9A8D4, #FCD34D, #6EE7B7, #7DD3FC, #C4B5FD, #F9A8D4) — rendered inside an absolutely positioned overflow-hidden rounded-full layer: a centered square (240% width, aspect-square) spins on an 8s linear infinite keyframe; nest the spinner one level deeper than the centering -translate-x/y-1/2 so the rotate animation never overrides the centering. Add a second identical spinning layer at -inset 4px with blur 7px and 60% opacity to bloom a soft pastel halo around the ring. Keep saturation pastel-low; the button face stays pure white with a gentle scale on hover (1.02) and press (0.97). Honor prefers-reduced-motion.
