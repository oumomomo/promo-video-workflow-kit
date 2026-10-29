# 方块变形

一个方块边旋转边在方形与圆形之间变形——高级仪表盘里那种 morphing loader。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/loader/ShapeShift.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React component called ShapeShift using React + Tailwind CSS + Framer Motion. A 28px square (h-7 w-7 bg-zinc-950) that runs a continuous morph cycle: animate rotate keyframes [0, 90, 180, 270, 360] together with borderRadius keyframes ['4px', '50%', '4px', '50%', '4px'] — square → circle → diamond → circle → square. Each quarter-cycle takes 1.6s (total duration 6.4s, times [0, 0.25, 0.5, 0.75, 1], easeInOut), repeating infinitely with smooth keyframes — the 'morphing loader' seen in premium dashboards. Transform/border-radius only. Respect prefers-reduced-motion by rendering the square static.
