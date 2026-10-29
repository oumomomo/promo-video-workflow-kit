# 光束描边

文章左侧一条 S 形曲线随滚动被墨水描绘，锌黑光点带光晕始终骑在墨迹最前端。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/scroll/TracingBeam.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：scroll

## 原始实现提示词

Create a React component called TracingBeam using React + Tailwind CSS + Framer Motion. Use the internal-scroll-container pattern: a 320px overflow-y auto viewport (overscroll-contain, thin custom scrollbar — page scroll never hijacked) holding a 900px article. The article (pl-16) has a mono uppercase caption, a semibold Chinese title, one intro line, then 4 sections, each with a small zinc-950 heading bar and 2–4 rounded placeholder text bars (h-2, zinc-200, varied widths) plus one bordered image placeholder block. Sticky beside it (pointer-events-none sticky top-0 h-0 wrapper, absolutely positioned at left-2 top-5) render a 40×280 rail: an SVG viewBox '0 0 40 280' with an S-curve path ('M 20 4 C 36 44, 4 76, 20 108 C 36 140, 4 172, 20 204 C 34 234, 8 254, 20 276') drawn twice — a zinc-200 track and a zinc-950 beam whose pathLength is bound directly to useScroll({ container }) scrollYProgress so the ink draws with scroll. Ride a glowing dot on the path head: a wrapper div with a blurred zinc-950/25 halo plus a 8px zinc-950 core, positioned by reading path.getTotalLength()/getPointAtLength(progress * len) inside useMotionValueEvent and writing the translate transform straight onto the element — zero re-renders. All useTransform input ranges strictly increasing within [0,1]. Include the sticky top progress hairline and the fading "向下滚动" hint.
