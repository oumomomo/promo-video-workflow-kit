# 单摆波

15 个白点以微妙不同的周期上下振荡，蛇形 → 双螺旋 → 混沌 → 完美同频，60 秒一轮回。数学的催眠之美。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/particle/PendulumWave.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React component called PendulumWave using React + plain Canvas 2D (no extra libraries). A dark (zinc-950) canvas fills its container (absolute inset-0, DPR-aware sizing via ResizeObserver, clamp DPR to 2). Draw 15 white glowing dots (3.2px radius, shadowBlur 8) in a horizontal row with 30px side padding, each oscillating vertically around the canvas midline with amplitude height/2 - 40. Dot i has period T_i = 60 / (51 + i) seconds, so over each 60-second cycle the row weaves through snake, double-helix and chaos patterns before returning to perfect unison. Connect the dots with a hairline polyline (rgba(255,255,255,0.22)) to reveal the emerging wave. Instead of clearing, fade the previous frame each tick with a translucent rect (rgba(9,9,11,0.08)) so the dots leave smooth motion trails; repaint a solid #09090B base on resize. Drive phases from performance.now() elapsed time. Clean up requestAnimationFrame and the ResizeObserver on unmount.
