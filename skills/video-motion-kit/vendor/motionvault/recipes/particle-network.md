# 星座网络

Canvas 粒子如星座般漂移，距离相近的节点自动连线；移动鼠标会轻轻吸引附近粒子。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/particle/ParticleNetwork.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：move

## 原始实现提示词

Create a React component called ParticleNetwork using React + plain Canvas 2D (no extra libraries). A canvas fills its container (absolute inset-0, cursor crosshair, DPR-aware sizing via ResizeObserver, clamp DPR to 2). Spawn nodes proportional to area (count = clamp(width*height/9000, 28, 70)) with small random velocities. Each frame: clear, update positions with velocity damping (0.995) and edge bounce, then draw hairline connections (rgba(9,9,11,0.12), 1px) between nodes closer than 110px with alpha fading by distance, and fill 1.6px dots (rgba(9,9,11,0.55)) at each node. Pointer interaction: nodes within 140px of the cursor receive a small attraction force toward it (acceleration 0.02 along the normalized direction); when the pointer leaves, reset it offscreen. Clean up requestAnimationFrame, ResizeObserver and listeners on unmount.
