# 波浪文字

每个字母像波浪一样持续起伏，轻盈活泼。悬停时波浪加速，离开后缓缓恢复。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/text/WaveTextPreview.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React wave-text component: each letter of the string continuously
oscillates vertically (±8px) following a sine wave — phase offset per letter
index × 0.35, period 1.6s, plus a subtle scale 1→1.08 in sync. Implement
with requestAnimationFrame or Framer Motion animate loops. On hover, double
the wave speed, easing back on leave. Tailwind styling.
