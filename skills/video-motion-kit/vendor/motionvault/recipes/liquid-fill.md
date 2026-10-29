# 液体填充

悬停时深色液体从底部涌起填满按钮，文字反白——饱满的转场感。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/button/LiquidFill.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：hover

## 原始实现提示词

Create a React liquid-fill button: an outlined button (1px zinc-950 border,
black text) that on hover fills from the bottom with black — the fill
layer's top edge is a gentle wave (SVG path or animated border-radius)
rising with translateY 100% → 0 over 0.5s ease-out, the wave subtly
undulating while hovered. The label flips to white after a 0.3s delay.
Reverse on mouse leave. Pure CSS + Tailwind.
