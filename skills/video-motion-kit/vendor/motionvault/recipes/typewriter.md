# 打字机

字符逐个敲出，光标闪烁，打完停顿后删除并切换下一句话。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/text/TypewriterPreview.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React typewriter component with TypeScript. It cycles through an
array of phrases: types each character at 90ms intervals, pauses 1.6s when
complete, deletes at 40ms per character, then types the next phrase. Render
a blinking block cursor (2px wide, 530ms blink) after the text. Pure React
state + setTimeout, no libraries. Tailwind styling, monospace optional.
