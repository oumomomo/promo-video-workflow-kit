# 钉住步骤切换

面板被钉在视窗中：左侧 UI 卡在三档阈值间渐变切换，右侧步骤说明滑过，当前步墨色高亮。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/scroll/PinnedSteps.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：scroll

## 原始实现提示词

Create a React component called PinnedSteps using React + Tailwind CSS + Framer Motion. Inside an internal scroll container (320px, overflow-y auto, overscroll-contain, thin scrollbar) place a 3.5×-tall track (1120px) with a sticky split panel. Left: a mock UI card (rounded-xl, border, soft shadow, window dots, big mono word DRAFT/BIND/SHIP, accent bar in muted sage/khaki/zinc) that morphs between three variants with a 300ms opacity+scale crossfade. Right: a masked column of three step descriptions (title + one line) that glides vertically in three steps via useTransform on useScroll({ container }) scrollYProgress with pauses at each stop. Derive the active index from scrollYProgress with useMotionValueEvent (threshold-only setState); the active step is zinc-950, inactive zinc-300, with 300ms color transitions. Add three indicator dots on the right edge (active: zinc-950, scale-125). Top progress hairline + fading "向下滚动" hint included.
