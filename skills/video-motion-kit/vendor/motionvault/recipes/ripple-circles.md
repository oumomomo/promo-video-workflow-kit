# 同心涟漪

点击处荡开三环同心细圈，错峰扩散后淡出；支持快速连击。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/background/RippleCircles.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：click

## 原始实现提示词

Create a React component called RippleCircles using React + Tailwind CSS + Framer Motion (Magic UI Ripple, click-triggered). The stage is an absolute inset-0 white container with cursor-pointer and role button. On pointerdown compute click coordinates via getBoundingClientRect and push a ripple {id, x, y} into state (cap at ~8 concurrent, slice off the oldest). Each ripple renders 3 thin concentric rings — motion.span h-24 w-24 rounded-full border border-zinc-400 positioned at left/top x/y — animating scale 0 → 3 with opacity 0.4 → 0 over 1.15s easeOut, staggered 150ms per ring (delay i*0.15). Center each ring with Framer Motion style x/y '-50%' (kept constant in both initial and animate) so centering never fights the scale. Prune the ripple from state in onAnimationComplete of the last ring. Rapid clicks stack freely. Add a centered pointer-events-none hint (zinc-900 title + mono 'CLICK TO RIPPLE' caption).
