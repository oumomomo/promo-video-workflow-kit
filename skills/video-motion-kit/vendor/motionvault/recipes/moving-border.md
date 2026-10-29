# 流动边框卡

一段明亮的锌黑沿圆角矩形的边界匀速巡游，带着一层柔光残影，周而复始。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/card/MovingBorderCard.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React component called MovingBorderCard using React + Tailwind CSS. Render a white card (288×176px, rounded-xl) with a minimal interior: a small mono uppercase label, a title, and a two-line muted description. Around it, a bright segment travels the rounded-rect perimeter endlessly: place an absolutely positioned SVG (viewBox matching the card size, inset-0, pointer-events-none) containing a single rect (1px inset, rx 11, fill none, pathLength 100, stroke #18181B zinc-900, strokeWidth 2, strokeLinecap round, strokeDasharray "14 86" for a short dash and long gap) and animate its stroke-dashoffset from 0 to -100 in a 4s linear infinite CSS keyframes loop. Duplicate the same SVG with strokeWidth 3, opacity 0.5 and a 4px blur as a soft glow copy trailing the crisp segment. Pause the animation with animation-play-state when the card scrolls out of view (IntersectionObserver). Isolate the looping SVG in a memoized micro-component. Pure CSS animation, transform-free, 60fps.
