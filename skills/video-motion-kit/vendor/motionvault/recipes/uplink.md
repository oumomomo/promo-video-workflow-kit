# 信号上行

五根信号强度的竖条逐级点亮又整体熄灭，顶端小箭头不断上滑淡出——正在上行传输中。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/loader/Uplink.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React component called Uplink using React + Tailwind CSS + Framer Motion. Center a column in the preview: on top a small lucide ArrowUp icon (h-3.5 w-3.5, strokeWidth 2.5, zinc-950) that each cycle slides y 4 → -7 while fading opacity 0 → 1 → 0 (1.4s, easeOut, times [0, 0.55, 1], infinite). Below it, a row of five signal-strength bars (w-1.5 rounded-full, items-end, 6px gap) with ascending heights 10/16/22/28/34px. Over a 1.4s infinite cycle each bar animates backgroundColor keyframes zinc-200 → zinc-950 → zinc-950 → zinc-200 (times [0, 0.18, 0.78, 1], easeInOut) with a 110ms stagger per bar (delay = i * 0.11) so they light up in sequence from weak to strong then all extinguish together. Gate all animations behind an IntersectionObserver in-view flag (render bars at zinc-200 and the arrow static when off-screen) and respect prefers-reduced-motion. Add a mono uppercase 'uplink' caption (11px, zinc-400) below.
