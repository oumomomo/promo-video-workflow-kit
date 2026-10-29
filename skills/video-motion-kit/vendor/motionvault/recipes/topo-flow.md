# 等高线流动

一片缓慢呼吸的噪声地形，marching squares 实时描出等高线，像地质图上的山脉在生长；鼠标划过会抬起一片高地。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/background/TopoFlow.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：move

## 原始实现提示词

Create a React component called TopoFlow using React + plain Canvas 2D (no extra libraries) over a white base. A canvas fills its container (absolute inset-0, DPR-aware sizing via ResizeObserver, clamp DPR to 2). Define an analytic pseudo-noise height field h(x,y,t) = sin(x*0.011 + t*0.16) * cos(y*0.013 - t*0.11) + 0.6*sin((x+y)*0.007 + t*0.23) + 0.4*cos((x-y)*0.009 - t*0.19) plus a pointer hill: a gaussian bump (sigma 110px, amplitude 0.9) at the smoothed cursor (lerp 0.1) that eases in while the pointer is inside. Each frame draw 9 contour levels (thresholds evenly spaced over the field range) via marching squares on a 10px sampling grid: for each cell evaluate h at the 4 corners, look up the 16-case table, and stroke the interpolated line segment(s) in zinc-700 rgba(63,63,70, alpha) with alpha rising per level (0.05 -> 0.22) so ridges read darker than valleys; highlight every 3rd level slightly (0.28 alpha, 1.2px) like index contours on a map. Recompute each frame for a living topographic map. Pure rAF loop; clean up the loop, ResizeObserver and listeners on unmount.
