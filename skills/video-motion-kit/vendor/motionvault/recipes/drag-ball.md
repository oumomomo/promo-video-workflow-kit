# 弹簧归位球

把 36px 的小黑球拖向任意角落——拖动中它沿速度方向拉成椭圆并拖着 3 层残影，松手后带着过冲弹簧飞回原点。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/spring/DragBall.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：move

## 原始实现提示词

Create a React component called DragBall using React + Tailwind CSS + Framer Motion, running entirely on MotionValues (zero setState). Inside a relative overflow-hidden preview, center a dashed zinc-300 origin ring (44px) and a draggable 36px ball (rounded-full, bg-zinc-950, cursor-grab, active:cursor-grabbing, touch-none). Position is driven by x/y MotionValues: the ball is a motion.div with drag, dragConstraints bound to the preview container ref, dragElastic 0.12, dragMomentum false, style={{ x, y }}. Velocity squash: take vx/vy from useVelocity(x/y) and derive three useTransforms — stretch = 1 + min(mag/1400, 0.5) for scaleX, squash = 1 - min(mag/5200, 0.18) for scaleY, angle = atan2(vy, vx) in degrees (only above a small 60px/s threshold) — applied to an INNER motion.span wrapping the visible ball so drag transform and squash transform never fight. Three ghost trails render behind the ball: memo-less children binding useSpring(x/y) with progressively lazier springs (stiffness 200/150/110, damping 20/18/18) at opacity 0.22/0.13/0.07. On drag end, fly home with animate(x, 0, { type: 'spring', stiffness: 180, damping: 12 }) and the same for y — a visible overshoot past the origin before settling. Light background, transform/opacity only.
