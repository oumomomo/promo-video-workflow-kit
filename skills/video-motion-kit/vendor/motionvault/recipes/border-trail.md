# 边框光点

圆角卡片轮廓上，一小段亮弧沿边框匀速循环描边，身后半圈处还有一段更淡的伴弧——pathLength + dashoffset 的经典戏法。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/svg/BorderTrailPreview.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React component called BorderTrail using React + Tailwind CSS + Framer Motion. It renders a 296x168px card: an absolutely-positioned SVG (viewBox 296x168) draws a rounded rect (x 1, y 1, width 294, height 166, rx 16) three times. First rect is the static base — white fill, 1px stroke #E4E4E7 (zinc-200). Second is the travelling bright arc: motion.rect with no fill, 1.5px stroke #09090B (zinc-950), round line cap, and the pathLength normalization trick — pathLength={100}, strokeDasharray '9 91', then animate strokeDashoffset from 0 to -100 over 3.2s with ease linear and repeat Infinity so a short bright segment orbits the border seamlessly. Third is a fainter companion arc half a lap behind: same rect, 1px stroke #A1A1AA (zinc-400), strokeDasharray '5 95', strokeDashoffset animating from -50 to -150 on the same 3.2s linear infinite timeline. Centered inside the card, static content: 'BORDER TRAIL' (14px mono, font-medium, uppercase, tracking 0.24em, zinc-950) over a small sub-caption 'STROKE-DASHOFFSET LOOP' (11px mono, uppercase, tracking 0.18em, zinc-400). Light background, animate stroke-dashoffset only, container aria-label.
