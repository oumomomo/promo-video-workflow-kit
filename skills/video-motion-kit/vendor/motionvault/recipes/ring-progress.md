# 环形进度

环形进度条扫到 78%，中心 mono 数字弹性同步计数，外圈点缀细密的刻度线。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/svg/RingProgressPreview.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React component called RingProgress using React + Tailwind CSS + Framer Motion. It renders a 160x160 SVG containing: a ring of 24 subtle tick marks (1px zinc-300 lines at radius 60-66, every 15deg, every 6th tick slightly longer), a track circle (radius 52, 6px stroke, zinc-200, no fill), and a progress arc — a motion.circle with the same radius, 6px zinc-950 stroke, round line cap, rotated -90deg around the center, animating pathLength 0 to 0.78 over 1.6s ease-out on mount. In the center, absolutely positioned, a mono-font number counts 0% to 78% in sync: drive a useMotionValue with animate() using a spring (stiffness 60, damping 16), round it via useTransform, and render it as the text content of a motion.span. Stop the animation controls on unmount. Light background, monochrome zinc only.
