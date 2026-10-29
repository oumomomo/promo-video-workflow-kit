# 手绘引导箭头

一条略带抖动的手绘弯曲线从左上绕到右下，1.2 秒画出、停留 1 秒、0.5 秒反向擦除，箭头头部在最后时刻补上，无限循环。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/svg/DrawArrowPreview.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React component called DrawArrow using React + Tailwind CSS + Framer Motion. It renders a 320x180 viewBox SVG containing a hand-drawn-feel guide arrow. The main curve is a slightly wobbly path from top-left winding to bottom-right: 'M 44 42 C 46 96 96 58 146 88 C 196 118 220 84 262 124', stroke #09090B (zinc-950), strokeWidth 3, round caps/joins, no fill. The arrowhead is a separate path of two short barbs at the tip: 'M 246 122 L 262 124 L 254 108', same stroke styling. Loop both on a 2.7s infinite repeat using pathLength keyframes: the curve animates [0, 1, 1, 0] with times [0, 0.44, 0.81, 1] and per-segment eases [easeInOut, linear, easeInOut] — 1.2s draw, 1s hold, 0.5s backward erase; the head animates [0, 0, 1, 1, 0] with times [0, 0.34, 0.44, 0.8, 1] so it flicks in during the last beat of the draw and erases with the tip. Center the svg (max-width ~360px) on a light background, animate pathLength only, container aria-label.
