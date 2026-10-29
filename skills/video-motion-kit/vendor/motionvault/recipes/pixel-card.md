# 像素涌动卡

卡片表面覆盖一层 8px 像素网格，悬停时像素块以随机延迟从指尖泛起又退去，像一波数字潮水。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/card/PixelCard.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：hover

## 原始实现提示词

Create a React component called PixelCard using React + Tailwind CSS + Canvas 2D. Render a white card (288×176px, rounded-xl, 1px zinc-200 border) with minimal content (mono uppercase label, title, two-line muted description). Overlay it with an absolutely positioned canvas (pointer-events-none, dimensions set via inline style, DPR-aware) divided into an 8px pixel grid (~36×22 cells). On pointerenter/pointermove track the cursor in card coordinates and run a requestAnimationFrame loop: each frame every cell computes phase = (t/1500ms + per-cell random seed*0.9 − distance-to-cursor/110) mod 1.1; cells with phase < 1 draw a zinc-900 square (inset 0.5px) whose opacity follows sin(phase × π) — a 0→1→0 pulse — so pixels ripple outward from the hovered point with random delays like a digital tide. Multiply by a global intensity that lerps toward 1 while hovering and 0 on leave; when intensity falls below 0.01 stop the rAF loop and clear the canvas. No React state in the pointer path — keep cursor position in refs.
