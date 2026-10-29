# 3D 倾斜卡片

卡片随鼠标在三维空间中倾斜，带一层跟随指针的高光，松手后弹性回正。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/card/TiltCard.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：move

## 原始实现提示词

Create a React component called TiltCard using React + Tailwind CSS + Framer Motion. Render a white card (rounded-xl, 1px zinc-200 border, subtle shadow) centered inside a wrapper with CSS perspective 800px. Track the pointer position over the card with onPointerMove, normalizing it to [0,1] on both axes, stored in useMotionValue and smoothed with useSpring (stiffness 180, damping 22). Derive rotateX in [10deg, -10deg] from the Y axis and rotateY in [-12deg, 12deg] from the X axis via useTransform, applied to the card with transformStyle preserve-3d. Add a glare layer: an absolutely positioned motion.div whose background is a radial-gradient(circle at x% y%, rgba(255,255,255,0.9), transparent 55%) with the gradient center following the pointer (also via useTransform, no useState in the pointer path). On pointer leave, animate both axes back to 0.5 so the card springs back to flat. Inner content uses translateZ(28px) for depth.
