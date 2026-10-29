# 聚焦卡组

横排三张小卡：悬停某张时它微微放大并清晰突出，其余两张模糊、缩小、变暗退后，弹簧过渡干脆利落。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/card/FocusCards.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：hover

## 原始实现提示词

Create a React component called FocusCards using React + Tailwind CSS + Framer Motion, recreating the Aceternity Focus Cards. Render three small cards (112×160px, rounded-xl, 1px zinc-200 border) in a horizontal row with 16px gaps; each card is a muted zinc gradient panel (light zinc-300 to darker zinc-500/600, all low-saturation) with a small white mono uppercase label and a short title. Track the hovered index in useState (null when none) on the row container's onPointerLeave / each card's onPointerEnter. Animate with Framer Motion's animate prop and a spring transition (type spring, stiffness 260, damping 22): the hovered card scales to 1.05 at full opacity with blur(0px); its siblings scale to 0.96, dim to opacity 0.5 and blur(4px) so they recede; with no hover all cards rest at scale 1, opacity 1, blur 0. Keep the row layout static (transforms only, no layout shift) and wrap the hover zone in a flex container so leaving the row resets every card together.
