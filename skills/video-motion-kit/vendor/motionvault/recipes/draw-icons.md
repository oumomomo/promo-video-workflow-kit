# 图标描绘

四个极简线性图标排在圆角小方块里，悬停任意一个，它的描边会依次画出；移开保持完成态，再次悬停重新描绘。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/svg/DrawIconsPreview.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：hover

## 原始实现提示词

Create a React component called DrawIcons using React + Tailwind CSS + Framer Motion. It renders a row of 4 minimal line icons — mountain+sun, wave, leaf, star — each inside a 56px rounded-xl tile with a 1px zinc-200 hairline border on white. Each icon is a 24x24 viewBox SVG made of 1-2 strokes (e.g. mountain: 'M3 18 L9 8 L13 14 L16 10 L21 18' plus a small circle for the sun; wave: two stacked sine curves; leaf: a closed leaf outline plus a vein; star: a 5-point star polygon path), stroke #09090B, strokeWidth 1.5, round caps, no fill. On mouse enter of a tile, increment a runId in that tile's state and key the svg on it so all strokes remount and draw sequentially: each motion.path (or motion.circle) animates pathLength 0 to 1, 300ms each, staggered by 120ms. On mouse leave do nothing — the icon stays fully drawn; hovering again re-runs the draw. Tiles are independent (own state), centered in a light preview with 16px gaps.
