# 沙漏翻转

两个三角对顶成的沙漏每 1.6 秒弹簧翻转 180°，内部沙面此消彼长——上面的流光，下面的堆满。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/loader/Hourglass.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React component called Hourglass using React + Tailwind CSS + Framer Motion. Center a 40×45 SVG hourglass (viewBox '0 0 32 36'): an outline drawn with one zinc-950 1.6px path — top cap 'M 5 2 H 27', bottom cap 'M 5 34 H 27', and two apex-to-apex triangles 'M 6 2 L 26 2 L 16 18 Z' / 'M 6 34 L 26 34 L 16 18 Z' (fill none, round joins). Inside, two zinc-950 sand polygons: the upper sand 'M 8.5,4.5 23.5,4.5 16,16.5' with transformBox fill-box and transformOrigin '50% 100%' draining scaleY 1 → 0, and the lower sand '8.5,31.5 23.5,31.5 16,19.5' with the same origin filling scaleY 0 → 1 — both over 1.05s with 0.45s delay, easeIn. A cycle counter state advances every 1.6s via setInterval in useEffect gated by an IntersectionObserver in-view flag; the whole SVG sits in a motion.div animating rotate to cycle * 180deg with a spring (stiffness 160, damping 15 — visible settle wobble), and the sand polygons are keyed by the cycle so they reset while the flip hides the swap. Loop forever. Respect prefers-reduced-motion by rendering a half-full static hourglass. Mono uppercase 'hourglass' caption (11px, zinc-400) below.
