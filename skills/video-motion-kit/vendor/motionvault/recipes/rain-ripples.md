# 雨落涟漪

深夜雨幕：细雨斜落水面，砸出一圈圈扩散又淡去的椭圆涟漪；点击落下一滴大雨，溅起三层同心涟漪与水花。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/particle/RainRipples.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：click

## 原始实现提示词

Create a React component called RainRipples using React + plain Canvas 2D (no extra libraries). A dark (zinc-950) canvas fills its container (absolute inset-0, cursor crosshair, DPR-aware sizing via ResizeObserver, clamp DPR to 2) with a faint horizon line (rgba(255,255,255,0.06)) at 70% height marking the water surface. Rain drops spawn at random x positions every 80-200ms and fall as short 6px white streaks (alpha 0.5, 11-15 px/frame); where each lands on the horizon, spawn an expanding ellipse ripple (radius 0 -> 46px, ry = 0.32 * radius for perspective, fading over 1.2s) plus a tiny 2-droplet splash. On click, a BIG drop (12px streak, brighter, accelerating to 14 px/frame) falls at the click x and lands at max(clickY, horizon + 6), producing 3 staggered concentric ripples (120ms apart, radius up to 64px) and a spray of 12 splash droplets in an upward fan with gravity 0.22. Quiet rainy-night mood, all strokes thin and white. Clean up requestAnimationFrame, ResizeObserver and listeners on unmount.
