# 视差光斑

五团低饱和的柔光色斑以不同深度随鼠标漂移，前后错落出细腻的多层空间感。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/background/ParallaxOrbs.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：move

## 原始实现提示词

Create a React component called ParallaxOrbs using React + Tailwind CSS (pure CSS/transforms, no canvas, no state re-renders on pointer move). Over a zinc-50 base, render 5 large absolutely positioned orbs (40-56% of the container, rounded-full) with soft radial-gradient fills in muted ~30%-saturation tones — sand hsl(38,32%,74%), sage hsl(140,22%,72%), sky hsl(205,38%,74%), rose hsl(350,38%,78%), lilac hsl(268,32%,78%) — each with filter blur(40px), sitting behind a small mock heading + button overlay. Each orb has a different depth factor (0.02, 0.04, 0.06, 0.08, 0.10): on pointermove compute the pointer offset from the container center, and in a rAF loop lerp each orb's current translation toward factor × offset with a 0.05 smoothing step, writing translate3d directly to el.style.transform (refs, never setState) so near orbs trail further than far ones — a subtle multi-plane depth effect. Reset targets to 0 on pointerleave; cancel the loop and listeners on unmount.
