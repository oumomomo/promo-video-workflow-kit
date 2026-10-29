# 双星环绕

两颗小点绕中心反向公转，身后拖着渐隐的彗尾——像一对互相追逐的星。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/loader/OrbitLoader.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React component called OrbitLoader using React + Tailwind CSS + Framer Motion. Two 8px zinc-950 dots orbit a center point in opposite directions (radius 18px, one revolution per 1.2s, linear infinite). Implement each orbiter as a zero-size motion.div at the center that rotates 0 → 360deg (the second 0 → -360deg, phase-offset by 180deg so they start opposite each other). Inside each rotator, render the main dot plus 6 ghost dots as a comet trail: each ghost sits 14deg further behind along the path with decreasing size (6.5 → 2.5px) and opacity (0.45 → 0.06), so the trail fades as the whole group spins. Add a tiny 4px zinc-300 dot at the center as the anchor point. Transform only. Respect prefers-reduced-motion by rendering two static dots.
