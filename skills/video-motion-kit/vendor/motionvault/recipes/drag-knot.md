# 可拖拽金属结

一颗抛光锌色金属环面结，按住拖拽即可甩动旋转，松手后带惯性滑行，静置 2 秒恢复慢速自转。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/threeD/DragKnot.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：move

## 原始实现提示词

Create a React component with React Three Fiber: a draggable polished
metal torus knot on a dark #09090B canvas. TorusKnot geometry (radius 1,
tube 0.32, 220x36 segments) with meshStandardMaterial zinc-300 #D4D4D8,
metalness 0.85, roughness 0.25. Pointer interaction with pointer capture:
while dragging, convert pointer delta (NDC) into angular velocity on both
axes (~4 rad per full-screen sweep); on release keep the inertia with
friction decay 0.95 per frame (frame-rate independent via pow(0.95, dt*60));
after 2s idle, lerp the yaw velocity back to a slow 0.25 rad/s auto-
rotation and pitch to 0. All motion state in refs, cursor grab/grabbing.
Lighting without network assets: drei Environment with resolution 256 and
3-4 Lightformers (top softbox intensity 3, two side strips, weak front
fill) plus ambient 0.15 — no HDR preset download.
