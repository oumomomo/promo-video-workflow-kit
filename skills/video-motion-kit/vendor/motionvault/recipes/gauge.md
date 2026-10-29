# 仪表盘

半圆仪表盘：指针弹簧摆动到 72% 并轻轻过冲回稳，弧轨与 12 根刻度随进度分段点亮，中心数字同步跳动。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/loader/GaugeLoader.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React component called GaugeLoader using React + Tailwind CSS + Framer Motion. Render a semicircular instrument gauge in a 220px container with an SVG viewBox '0 0 200 116', center pivot at (100, 100). Draw a 180° arc track (path 'M 10 100 A 90 90 0 0 1 190 100', stroke zinc-200, width 3, round caps) plus an identical zinc-950 progress arc bound via style pathLength to a clamped MotionValue. Add 12 tick marks (lines from r=78 to r=90) sweeping left → right; render each tick twice — a static zinc-300 base and a zinc-950 overlay whose opacity maps the gauge value over [t-0.02, t] (t = i/11) so segments light up as the needle passes. The needle is a 3px zinc-950 line from the pivot to r=66 inside a motion.g whose rotate maps value [0,1] → [-90deg, 90deg] with transformOrigin '100px 100px'; add a zinc-950 hub circle with a white center dot. Drive a single useMotionValue(0) with animate(mv, 0.72, { type: 'spring', stiffness: 120, damping: 14 }) on mount (gated by an IntersectionObserver in-view flag, reset to 0 when scrolled out) so the needle visibly overshoots then settles at 72%. Center a mono readout (22px semibold number + small zinc-400 '%') bound via useTransform(v => round(v*100)) as a MotionValue child — zero re-renders. Mono 'gauge' caption below. With prefers-reduced-motion jump straight to 72%.
