# 发光边框卡

一圈渐变光沿卡片边框缓缓流动，像被点亮的轮廓。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/card/GlowBorderCard.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React glow-border card: wrap the card in a pseudo-element border
(1.5px) painted with a conic-gradient (transparent → #6366F1 → transparent,
25% arc) whose angle rotates 360deg every 4s (use CSS @property --angle or a
rotating background layer masked to the border ring). Add a matching blurred
glow behind it at 0.4 opacity. On hover, speed up to 2s per revolution.
