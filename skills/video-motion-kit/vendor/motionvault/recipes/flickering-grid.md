# 网格明灭

规整的浅色网格之上，随机方格如城市灯火般轻轻点亮又熄灭；中央标题验证可读性。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/background/FlickeringGrid.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React component called FlickeringGrid using React + Tailwind CSS + scoped CSS keyframes (no canvas). Draw a regular square grid (36px cells, 1px lines at rgba(24,24,27,0.05) via two repeating linear-gradient backgrounds) over white. Every ~420ms spawn 1-2 random cells — small rounded squares inset 3px inside a grid cell, fill rgba(113,113,122,alpha) with a random peak alpha 0.18-0.48 — that each play a one-shot CSS pulse keyframe (opacity 0 to 1 at 42% back to 0, with a subtle scale 0.7 to 1 to 0.85) over a random 0.9-2.5s duration, then get pruned from state; cap ~16 cells alive, like distant city lights flickering. Measure the container with a ResizeObserver to compute grid columns/rows. Overlay a centered mock heading (zinc-900 title plus a small mono caption, pointer-events-none) to prove foreground text stays readable over the effect. Honor prefers-reduced-motion.
