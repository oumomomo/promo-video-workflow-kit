# 文字呼吸

「加载中…」六个字符依次明暗呼吸——安静克制，适合任何等待角落。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/loader/TextPulse.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React component called TextPulse using React + Tailwind CSS + Framer Motion. Render the text '加载中' followed by three dots as six inline-block characters in JetBrains Mono style (font-mono, text-sm / 14px, tracking wide, text-zinc-600). Each character pulses its opacity through keyframes [0.25, 1, 0.25] over a 900ms cycle with easeInOut, repeating infinitely, staggered by 150ms per character (delay = index * 0.15) so the brightness sweeps calmly from left to right like breathing. Opacity only. Respect prefers-reduced-motion by rendering the text static.
