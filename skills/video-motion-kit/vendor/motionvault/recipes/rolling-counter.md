# 滚动数字

里程表式数字滚动：进入视口时每位数字从 0 开始向上翻滚到目标值，弹簧缓动、位间错峰 100ms。点击卡片或 Replay 重播。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/text/RollingCounterPreview.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：click

## 原始实现提示词

Create a React component called RollingCounter using React + Tailwind CSS + Framer Motion. It shows a row of 2-3 stats (e.g. 52 收录效果 / 07 效果分类 / 6 交互方式): big mono digits (~44px, zinc-950) with a small 12px zinc-400 label under each. Each digit is an odometer column: an overflow-hidden viewport (height 56px) containing a vertical strip of digits 0-9 (each row 56px tall, flex-centered). On mount the strip springs from translateY 0 to translateY(-target * 56px) with a spring of stiffness 80 and damping 20, with a 100ms delay stagger between digit columns left-to-right, so numbers roll up from 0 like a slot machine settling. Trigger on entering the viewport (IntersectionObserver or mount gating), and replay on click: wrap the strips with a key derived from a run counter incremented by onClick on the container (role=button, keyboard Enter/Space support). The digits animate transform only; use will-change-transform. Light background, aria-label announces each stat value plus label.
