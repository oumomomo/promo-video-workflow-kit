# 弹性开关

滑块在滑动途中被拉成椭圆再弹回圆形，像一颗有弹性的软糖；轨道颜色随之渐变。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/spring/ElasticToggle.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：click

## 原始实现提示词

Create a React component called ElasticToggle using React + Tailwind CSS + Framer Motion + the Sun and Moon icons from lucide-react. A toggle switch (role='switch'): a 56×32 rounded-full track that tweens its background zinc-200 ⇄ zinc-950 over 250ms, with a 24px white knob (rounded-full, shadow-sm). The knob slides x 0 → 24 on a spring (stiffness 500, damping 28). While sliding the knob STRETCHES: nest the visible knob inside the sliding wrapper and drive it with useAnimationControls on every toggle — scaleX keyframes [1, 1.4, 1] and scaleY [1, 0.78, 1] over 450ms (times [0, 0.45, 1], easeOut) so it becomes a horizontal ellipse mid-travel then squashes back. Bonus: tiny 12px sun/moon icons crossfade inside the knob (opacity + scale + ±90° rotate, 200ms) — sun when off, moon when on. Transform/opacity only, centered on a light preview.
