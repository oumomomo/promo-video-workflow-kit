# 磁吸卡

鼠标靠近时卡片被轻轻吸向光标，离开后被弹回原位。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/card/MagneticCard.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：move

## 原始实现提示词

Create a React magnetic card with Framer Motion: while the cursor is inside
the container, translate the card toward the cursor with distance-based
falloff (max 24px) using useMotionValue + useSpring (stiffness 200,
damping 18). On mouse leave, spring back to origin with a satisfying
overshoot. Apply the same magnetic effect at 0.5x strength to the card's
inner content for parallax depth.
