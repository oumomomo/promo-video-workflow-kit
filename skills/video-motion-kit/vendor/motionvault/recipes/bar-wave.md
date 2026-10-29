# 音浪条

五根圆角竖条像均衡器一样起伏，中间最高——把等待变成一小段律动。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/loader/BarWave.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React component called BarWave using React + Tailwind CSS + Framer Motion. Five vertical bars in a row (w-1 rounded-full bg-zinc-800, 6px gap, transformOrigin center) with heights peaking in the middle: 24, 32, 40, 32, 24px. Each bar animates scaleY keyframes [0.3, 1, 0.3] over 900ms with easeInOut, repeating infinitely, staggered by 100ms per bar (delay = index * 0.1) so the wave ripples left to right like an equalizer. Transform only. Respect prefers-reduced-motion by rendering the bars static.
