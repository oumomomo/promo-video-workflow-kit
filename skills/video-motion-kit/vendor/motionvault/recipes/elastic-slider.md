# 弹性滑块

拖拽手柄时它沿拖拽方向被拉扁，轨道填充像跟屁虫一样滞后半拍地弹过来，松手瞬间手柄果冻式回弹归位。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/spring/ElasticSlider.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：move

## 原始实现提示词

Create a React component called ElasticSlider using React + Tailwind CSS + Framer Motion. A horizontal slider inside a light preview: a 4px rounded-full zinc-200 track (flex-1), a zinc-950 fill bar, a 24px white knob (rounded-full, subtle border + shadow-sm, cursor-grab), and a mono numeric readout (0-100) on the right. Drive the knob with a MotionValue x bound to drag (drag='x', dragConstraints { left: 0, right: trackWidth - 24 } measured via ResizeObserver, dragElastic 0, dragMomentum false). The fill does NOT track x directly — it follows useSpring(x, { stiffness: 140, damping: 22, mass: 0.8 }) so it lags elastically behind the knob, rendered as percentage width via useTransform. While dragging, the knob stretches in the drag direction (scaleX 1.3, scaleY 0.85, 150ms easeOut); on drag end it jelly-bounces back with keyframes scaleX [1.3, 1] / scaleY [0.85, 1] on a spring (stiffness 500, damping 12). Pointer-down on the track springs the knob to that position (animate(x, target, { type: 'spring', stiffness 400, damping 30 })) with the same squash keyframes. Render the readout by passing a rounded useTransform MotionValue directly as a motion.span child — zero per-frame setState.
