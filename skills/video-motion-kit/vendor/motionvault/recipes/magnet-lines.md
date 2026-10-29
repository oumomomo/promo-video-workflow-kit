# 磁吸线阵

9×5 的短线阵列，每根线用弹簧平滑转向指针方向，离指针越近拉得越长、颜色越深；指针离开后缓缓回正。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/spring/MagnetLines.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：move

## 原始实现提示词

Create a React component called MagnetLines using React + Tailwind CSS + Framer Motion, running entirely on MotionValues (zero setState). Render a 9×5 grid (gap 30px, fixed pixel size ~270×150) of short 12px lines (h-[2px], rounded-full, zinc-400). onPointerMove on the grid wrapper writes pointer coords (relative to the wrapper rect) into mx/my MotionValues and sets an 'active' MotionValue to 1; onPointerLeave sets active to 0. Each line is a child component receiving mx/my/active plus its cell center (cx, cy): compute the target angle with useTransform([mx, my, active]) — atan2(y-cy, x-cx) in degrees while active, 0 when idle — then smooth it through useSpring(angle, { stiffness: 180, damping: 16 }) bound to the line's rotate style, so lines swivel toward the cursor and ease back upright on leave. Distance effects come from a second useTransform producing the pointer distance (9999 when idle): scaleX = useTransform(dist, [40, 220], [1.7, 1]) softened by another spring (stiffness 200, damping 20), and backgroundColor = useTransform(dist, [40, 220], ['#09090B', '#A1A1AA']) so nearby lines stretch longer and darken to zinc-950. Position each line absolutely at its cell center, cursor-crosshair on the wrapper, light background, container aria-label.
