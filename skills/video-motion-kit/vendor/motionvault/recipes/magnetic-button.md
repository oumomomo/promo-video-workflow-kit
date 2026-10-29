# 磁吸按钮

鼠标靠近时按钮被吸附过去，文字以更小幅度跟随，形成双层视差。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/button/MagneticButton.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：move

## 原始实现提示词

Create a React magnetic button with Framer Motion: when the cursor comes
within 80px, the whole pill button translates toward it (max 16px) via
useMotionValue + useSpring (stiffness 180, damping 14); the inner label
follows at 0.4x strength for layered parallax. On leave, both spring back
with a soft overshoot. Attach listeners on a wrapper, not window.
