# 水下焦散

阳光穿过水面在池底投下流动的光网——Voronoi 焦散缓缓聚散明灭，一池安静的波光。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/background/Caustics.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React component called Caustics using React + plain Canvas 2D (no extra libraries). A deep water-blue canvas (#0B1B2A) fills its container (absolute inset-0, DPR-aware sizing via ResizeObserver, clamp DPR to 2). Simulate swimming-pool light caustics with a jittered Voronoi approach: scatter a grid of seed points (spacing 64px, each jittered ±22px, drifting slowly on individual sine orbits of 8-14px amplitude, periods 5-11s). Each frame, on a coarse render buffer (scale 0.25, ImageData), compute for each pixel the distances to the two nearest seeds (F1, F2) by checking only the 3x3 neighboring cells; intensity = clamp01(1 - (F2 - F1) / 26) ^ 2.6 — bright thin webs where seeds are equidistant. Map intensity to a pale aqua (140, 220, 210) tint added over the base, plus a faint vertical light gradient (deeper = darker). Upscale the buffer with drawImage (smoothing on) so edges stay soft. Slow, hypnotic, never flashy: cap intensity at 0.5 alpha. Pure rAF loop; clean up the loop and ResizeObserver on unmount.
