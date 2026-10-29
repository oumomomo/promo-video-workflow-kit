# 聚光灯卡片

鼠标所到之处亮起一圈柔和的径向光晕，黑暗中摸索的质感（预览窗用深色底）。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/card/SpotlightCard.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：move

## 原始实现提示词

Create a React spotlight card: a dark card (zinc-900 on zinc-950) with a
radial-gradient spotlight (radius 220px, white at 8% opacity fading to
transparent) that follows the cursor via CSS custom properties --x/--y
updated on mousemove. Also brighten the 1px border near the cursor using a
masked gradient border. Smooth, GPU-friendly (transform/opacity only).
