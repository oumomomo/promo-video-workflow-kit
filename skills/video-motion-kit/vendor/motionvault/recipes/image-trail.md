# 移动残影

快速移动鼠标时轨迹上留下小圆点与小方块残影，各自弹出后缩放淡出 0.8 秒；速度低于阈值则一片安静。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/particle/ImageTrail.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：move

## 原始实现提示词

Create a React component called ImageTrail using React + plain Canvas 2D (no extra libraries). A light canvas fills its container (absolute inset-0, cursor crosshair, DPR-aware sizing via ResizeObserver, clamp DPR to 1.75). On pointermove compute cursor speed (dist/dt in px/ms); only when speed exceeds ~0.9 px/ms AND distance from the last spawn exceeds 14px, stamp one ghost at the cursor: alternate circles and squares, size 9-23px, random rotation, mostly zinc greys (#A1A1AA/#71717A/#52525B/#D4D4D8) with a ~10% chance of amber #F59E0B. Each ghost lives 800ms: scale pops in over the first 110ms, then shrinks to 65% while alpha fades 0.9 to 0; draw squares via save/translate/rotate/fillRect. Cap the live list at 60 ghosts (drop oldest). Slow movement spawns nothing. Clean up requestAnimationFrame, ResizeObserver and listeners on unmount.
