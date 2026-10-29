# 流沙堆积

顶部流沙倾泻而下，沙粒按元胞自动机规则下落、侧滑、堆成沙丘；按住鼠标从指间漏沙，点击沙丘会把它搅塌。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/particle/SandPile.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：move

## 原始实现提示词

Create a React component called SandPile using React + plain Canvas 2D (no extra libraries). A light (zinc-50 #FAFAFA) canvas fills its container (absolute inset-0, DPR-aware sizing via ResizeObserver, clamp DPR to 2). Run a falling-sand cellular automaton on a coarse grid (cell 5px, stored in a Uint8Array, updated bottom-up each tick): a grain falls straight down if the cell below is empty, else slides down-left or down-right (random order) if empty, else rests — piles grow natural ~34-degree angle-of-repose slopes. Three fixed spouts near the top (at 25% / 50% / 75% width) each emit a thin stream (spawn a grain with 60% probability per tick in a 2-cell-wide nozzle). Render grains as filled rects in warm sand tones (amber-200 #FDE68A / amber-300 #FCD34D / amber-400 #FBBF24 picked per grain) over a faint zinc-100 ground shadow. Pointer: while the pointer is down (or moving with buttons pressed), pour a stream from the cursor (3-cell-wide nozzle, 90% per tick); on a single click without drag, excavate — clear grains in a 5-cell radius so slopes collapse and re-settle. Cap live grains at ~5200 (stop spouts when full); every 14s quietly dissolve the bottom row to make room. Pure rAF loop (tick the automaton every other frame for a calm pace); clean up the loop, ResizeObserver and listeners on unmount.
