# 烟雾流动

数百条短痕顺着缓慢演化的流场漂移，帧与帧之间用半透明暗纱覆盖——轨迹像烟一样化开；鼠标划过会搅起一小团涡旋。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/particle/SmokeFlow.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：move

## 原始实现提示词

Create a React component called SmokeFlow using React + plain Canvas 2D (no extra libraries). A dark (zinc-950 #09090B) canvas fills its container (absolute inset-0, cursor crosshair, DPR-aware sizing via ResizeObserver, clamp DPR to 2). Spawn 380 motes advected by a smooth analytic flow field approximating curl noise: angle(x,y,t) = (sin(x*s*1.7 + t*0.31) + cos(y*s*2.3 - t*0.23) + sin((x+y)*s*0.9 + t*0.12) + cos((x-y)*s*1.3 - t*0.17)) * PI/2.2 with s = 0.0021 and t in seconds; each mote moves along the field at 0.35-1.1 px/frame. NEVER clearRect: each frame paint a translucent veil rgba(9,9,11,0.055) so motion leaves dissolving smoke trails. Draw each mote as a short round-capped line segment (1.1px) from its previous to current position in muted slate tones (148,163,184 / 113,125,150 / 100,116,139 / 203,213,225) at ~0.34 alpha scaled by a lifetime envelope (fade in over 40 frames, out over the last 60 of a 260-580 frame life), then respawn at a random position. While the pointer is inside, stir a local vortex: motes within 130px get a tangential push (2.4 px/frame with linear falloff). Repaint a solid #09090B base on resize. Clean up requestAnimationFrame, ResizeObserver and listeners on unmount.
