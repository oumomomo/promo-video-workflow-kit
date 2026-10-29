# 鼠标点亮网格

鼠标经过之处，浅色点阵下浮出一层深色网格——Linear 式的精确与克制。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/background/SpotlightGrid.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：move

## 原始实现提示词

Create a React component called SpotlightGrid using React + Tailwind CSS (pure CSS, no canvas, no state re-renders on pointer move). A full-bleed absolute inset-0 container over white renders two stacked layers of the same dot grid (small dots at intersections, 28px spacing, built with a repeating radial-gradient background). The base layer uses zinc-200 dots; the top layer uses slightly larger zinc-800 dots and is revealed only through a radial-gradient mask (circle 180px) centered on the pointer. The mask position follows CSS variables --x/--y updated directly via el.style.setProperty in a pointermove handler (initialize offscreen at -9999px, reset on pointerleave) so moving the mouse never triggers a React re-render — Linear.app-style precision feel. Set both maskImage and WebkitMaskImage.
