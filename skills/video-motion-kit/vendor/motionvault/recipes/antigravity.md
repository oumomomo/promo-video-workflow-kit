# 失重粒子

40 个小圆点失重般静止漂浮，鼠标靠近时被平方衰减的斥力推开，远离后弹簧缓缓归位。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/particle/Antigravity.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：move

## 原始实现提示词

Create a React component called Antigravity using React + plain Canvas 2D (no extra libraries). A light canvas fills its container (absolute inset-0, cursor crosshair, DPR-aware sizing via ResizeObserver, clamp DPR to 1.75). Place 40 dots (radius 2.2-4px, zinc-500 #71717A at 0.85 alpha) at random home positions with a 30px margin; each dot keeps home, current position and velocity. Per frame: if the cursor is within 150px, apply inverse-square repulsion f = min(0.9, 1400/dist^2) along the direction away from the cursor; always apply a soft spring toward home (v += (home-pos)*0.012) and damping (v *= 0.92). Dots displaced more than 14px render darker (zinc-600 #52525B), and each home position shows a faint 1.2px anchor dot at 0.12 alpha so the field reads even before interaction. Reset the pointer offscreen on leave. Clean up requestAnimationFrame, ResizeObserver and listeners on unmount.
