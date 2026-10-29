# 全息眩光卡

深色卡片随鼠标在三维空间倾斜，一层低饱和的彩虹全息眩光随指针流转，像收藏卡的镭射面，克制而高级。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/card/HoloCard.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：move

## 原始实现提示词

Create a React component called HoloCard using React + Tailwind CSS + Framer Motion. Render a dark card (zinc-900, rounded-2xl, 1px zinc-800 border) centered inside a wrapper with CSS perspective 900px. Track the pointer over the card with onPointerMove, normalize to [0,1] on both axes into useMotionValue, and smooth with useSpring (stiffness 180, damping 22). Derive rotateX in [10deg, -10deg] and rotateY in [-10deg, 10deg] via useTransform, applied with transformStyle preserve-3d; on pointer leave, spring both axes back to 0.5. Layer a holographic glare: an absolutely positioned motion.div with mix-blend color-dodge whose backgroundImage is a soft spectrum linear-gradient at 115deg (transparent → pink/amber/mint/sky/violet at ~0.35 alpha → transparent), backgroundSize 250% 250%, and backgroundPosition counter-following the pointer via useTransform — never neon, always tasteful. Add a faint diagonal shine band: a rotated (20deg) motion.div with a white 12% linear-gradient streak whose translateX sweeps across the card with the pointer. Fade both glare layers in only while hovering (spring a hover MotionValue 0→1). Content stays minimal: small mono uppercase label, a short title, and a CSS-only orb (radial-gradient sphere with a 1px white/10 ring) floating at translateZ(30px).
