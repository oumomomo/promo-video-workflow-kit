# 像素轨迹

鼠标经过的 8px 网格落下一枚枚像素方块，落格即定格、1.2 秒渐隐，连续移动画出一条虚线像素蛇。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/particle/PixelTrail.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：move

## 原始实现提示词

Create a React component called PixelTrail using React + plain Canvas 2D (no extra libraries). A light canvas fills its container (absolute inset-0, cursor crosshair, DPR-aware sizing via ResizeObserver, clamp DPR to 1.75). The pointer stamps an 8px grid: on pointermove snap the cursor to cell (floor(x/8), floor(y/8)) and record it in a Map keyed "cx,cy" with a birth time; skip re-stamping a cell that is less than half-way through its life. Each cell draws as a 7x7px square (0.5px inset hairline gap) fading from 0.9 alpha to 0 over 1200ms, then is deleted — continuous movement leaves a dashed snake of pixels. Colors: mostly zinc-800 #27272A with some zinc-700/zinc-600, ~8% amber #F59E0B. Cap the map at 240 cells (evict oldest). Clean up requestAnimationFrame, ResizeObserver and listeners on unmount.
