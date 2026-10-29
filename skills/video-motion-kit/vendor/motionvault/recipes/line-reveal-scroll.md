# 逐行揭示

六行文字各自藏在 overflow-hidden 遮罩里，随滚动逐行从 110% 下方揭面升起，行内的轻微模糊同步散去。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/scroll/LineRevealScroll.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：scroll

## 原始实现提示词

Create a React component called LineRevealScroll using React + Tailwind CSS + Framer Motion. Use the internal-scroll-container pattern: a 320px overflow-y auto viewport (overscroll-contain, thin custom scrollbar — never hijack page scroll) with a 760px track and a sticky full-viewport padded panel (px-9). Center a mono uppercase 'LINE BY LINE' caption, then six lines of Chinese text at 19px font-medium tracking-wide zinc-950. Each line is wrapped in its own overflow-hidden mask div (py-0.5); the inner motion.p binds useScroll({ container }) scrollYProgress via useTransform over its own strictly-increasing slice — line i maps [0.06 + i*0.13, 0.06 + i*0.13 + 0.16] to y ['110%', '0%'], plus filter 'blur(6px)' → 'blur(0px)' over the last two-thirds of the slice and opacity 0 → 1 over the first 0.04 — so lines surface one after another, rising out of the mask while the blur clears (distinct from per-character opacity lighting). End with a faint mono footnote '06 LINES · MASKED REVEAL'. Pure MotionValue bindings, zero re-renders, clamp default on. Top progress hairline + fading "向下滚动" hint included.
