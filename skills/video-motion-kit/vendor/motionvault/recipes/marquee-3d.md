# 立体滚动卡墙

CSS 3D 透视下的四列卡片墙垂直无限滚动，方向交错、速度各异，上下边缘渐隐。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/threeD/Marquee3D.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React component with Tailwind CSS (pure DOM, no WebGL): a 3D
marquee card wall. Inside a preview container, a perspective(900px) stage
holds a plane rotated rotateX(18deg) rotateZ(-10deg) containing 4 vertical
columns of small mock cards (white bg, hairline zinc-200 borders, soft
neutral gradient thumbnails with one subtle amber accent, tiny skeleton
title/text bars and mono tag chips). Each column scrolls vertically in an
infinite seamless loop (duplicate the card list, animate translateY 0 to
-50% with transform-only keyframes), alternating directions at slightly
different durations between 18s and 28s. Fade top and bottom edges with a
mask-image linear gradient, offset columns with small translateZ values for
parallax depth, and isolate each looping column in a React.memo component.
