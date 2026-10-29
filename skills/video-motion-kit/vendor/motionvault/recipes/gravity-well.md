# 引力井

150 粒星尘缓缓漂移，鼠标化作引力井——靠近的粒子被捕获成环绕轨道；点击瞬间井变斥力场，粒子四散炸开。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/particle/GravityWell.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：click

## 原始实现提示词

Create a React component called GravityWell using React + plain Canvas 2D (no extra libraries). A dark canvas fills its container (absolute inset-0, cursor crosshair, DPR-aware sizing via ResizeObserver, clamp DPR to 2). Spawn 150 small white particles (1-2.4px, alpha 0.35-0.85) drifting slowly (0.15-0.45 px/frame) and wrapping around edges. While the pointer is inside, it acts as a gravity well: particles within 200px receive a mild attraction toward the cursor (acceleration ~0.045 with distance falloff) plus a stronger tangential push (~0.14 perpendicular to the radial direction) so they are captured into ORBITS instead of collapsing; add an outward push inside 34px, global velocity damping 0.985 and a 4 px/frame speed cap for stability. Draw a faint 200px reach circle and a 6px core ring at the cursor. On click, the well becomes a repulsor for 400ms: particles within 260px are blasted outward (force 3.2 with falloff), an expanding flash ring (10 -> 120px, fading over 400ms) marks the pulse, then calm orbiting resumes. Reset the pointer offscreen on pointerleave. Clean up requestAnimationFrame, ResizeObserver and all listeners on unmount.
