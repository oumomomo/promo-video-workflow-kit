# 多层视差卡

卡片整体随指针轻倾，内部三层内容按 0.3× / 0.6× / 1.0× 的深度差速移动，扁平卡片里长出真实的纵深感。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/card/TiltParallaxCard.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：move

## 原始实现提示词

Create a React component called TiltParallaxCard using React + Tailwind CSS + Framer Motion. Render a white card (288×192px, rounded-2xl, 1px zinc-200 border, soft shadow, overflow hidden) centered in a wrapper with CSS perspective 900px. Track the pointer with onPointerMove, normalize to [-1,1] on both axes into useMotionValue, smooth with useSpring (stiffness 160, damping 20), and derive rotateX/rotateY in ±8deg via useTransform, applied with transformStyle preserve-3d; spring back to 0 on pointer leave. Inside, translate three layers at different depths, all bound to the same springs with no setState in the pointer path: a background layer (two soft blurred gradient blobs, indigo-200/60 and rose-200/60) moving at 0.3× (±9px, translateZ 0), a mid content card (white/85 backdrop-blur inner panel with skeleton lines) at 0.6× (±18px, translateZ 30px), and a foreground badge + title (black pill chip with mono uppercase text plus a semibold title) at 1.0× (±30px, translateZ 60px). Finish with a soft glare sweep: an absolutely positioned motion.div whose radial-gradient highlight (white 0.85 fading to transparent at 55%) follows the pointer via useTransform, sitting at translateZ 80px.
