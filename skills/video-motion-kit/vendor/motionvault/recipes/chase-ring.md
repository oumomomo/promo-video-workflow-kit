# 双弧追逐

同一圆环上两段缺口圆弧反向匀速旋转，长弧的缺口还会呼吸伸缩——短弧永远在追，永远差一点。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/loader/ChaseRing.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React component called ChaseRing using React + Tailwind CSS + Framer Motion. Center a 56px SVG (viewBox '0 0 64 64') with a faint full-circle track (r 26, stroke zinc-100, width 3). On the same ring render two gapped arcs (circumference ≈ 163.4): the LONG arc is a zinc-950 round-cap circle with an animated strokeDasharray breathing between '120 43.4' and '70 93.4' and back (2.4s easeInOut infinite), wrapped in a motion.g (transformBox fill-box, origin center) rotating 0 → 360deg over 1.2s linear infinite, clockwise. The SHORT arc is a zinc-400 round-cap circle with a fixed dasharray '34 129.4' and dashoffset -60, inside another motion.g rotating 0 → -360deg over 0.9s linear infinite — counter-clockwise, slightly faster, so it forever chases the long arc while the long arc's gap breathes. Gate all animations behind an IntersectionObserver in-view flag (render statically when off-screen) and respect prefers-reduced-motion. Mono uppercase 'chase ring' caption (11px, zinc-400) below.
