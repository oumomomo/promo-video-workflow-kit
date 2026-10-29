# 像素雪

深蓝黑夜里方形像素雪花以不同速度飘落、水平轻摆，近地处淡出仿佛悄悄积起一层雪。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/particle/PixelSnow.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React component called PixelSnow using React + plain Canvas 2D (no extra libraries). A dark (zinc-950) canvas fills its container (absolute inset-0, DPR-aware sizing via ResizeObserver, clamp DPR to 2). Spawn square pixel flakes (2, 3 or 4 px, fillRect, no arcs) with count scaling to container width (clamp(width/6, 40, 140)). Each flake falls at 0.35-1.2 px/frame, sways horizontally on a sine (amplitude 4-18px, period 2.4-6s, random phase), and has its own whiteness (lerp channel value 212-255) and alpha (0.35-0.95). Paint a soft bottom gradient (rgba(228,228,231,0) to 0.14 over the bottom ~14px) suggesting an accumulated snow layer; flakes fade out over the last 40px above that ground line, then respawn just above the top edge with fresh random parameters. Clean up requestAnimationFrame and the ResizeObserver on unmount.
