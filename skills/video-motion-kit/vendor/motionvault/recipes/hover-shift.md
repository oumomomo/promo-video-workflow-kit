# 悬停错位按钮

悬停时原文案上滑离场，带箭头的新文案从下方滑入，底色同步变浅一档。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/button/HoverShift.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：hover

## 原始实现提示词

Create a React component called HoverShift using React + Tailwind CSS (pure CSS group-hover, no JS animation — Magic UI Interactive Hover Button, restrained). A dark button (h-11, rounded-lg, px-8, text-sm white, overflow-hidden) whose background transitions zinc-950 → zinc-800 on hover. Inside, the resting label '开始使用' sits in normal flow; a duplicate overlay label '进入文档' with a lucide ArrowRight icon is absolutely positioned over the button, pre-translated translate-y-[180%]. On group-hover both spans share one 0.3s cubic-bezier(0.22,1,0.36,1) transform transition: the original slides up and out (-translate-y-[180%]) while the overlay slides in to translate-y-0 — a clean vertical text swap through the overflow window. Add active:scale-[0.97] for press feedback. Transform + background-color only.
