# 烟花绽放

点击任意处，一枚烟花呼啸升空后炸开成放射状星火；静置几秒会自动补一发。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/particle/Fireworks.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：click

## 原始实现提示词

Create a React component called Fireworks using React + plain Canvas 2D (no extra libraries). A dark canvas fills its container (absolute inset-0, cursor crosshair, DPR-aware sizing via ResizeObserver, clamp DPR to 2). On click, launch a rocket from the bottom edge that rises to the click point (speed ~8-10 px/frame upward, slight horizontal sine wobble of 3px amplitude, short 8-dot fading trail, glowing white head). On arrival it explodes into 60-90 radial sparks using 2-3 harmonious hues per burst picked from a muted palette (amber #F59E0B/#FBBF24/#FDE68A, rose #F43F5E/#FB7185/#FDA4AF, sky #0EA5E9/#38BDF8/#7DD3FC). Sparks have random radial velocities (1-5 px/frame), gravity 0.04, drag 0.96, and fade over ~1.5s while their radius shrinks to 30%. If no launch happens for 2.5s, auto-launch one rocket at a random position. Multiple simultaneous bursts must be supported. Clean up requestAnimationFrame, ResizeObserver and listeners on unmount.
