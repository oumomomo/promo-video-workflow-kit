# 悬停字母弹跳

悬停任意字母，它带着弹簧感跳起，相邻字母被轻微带起 15%，像橡皮筋一样牵连。离开后弹回原位。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/text/LetterHoverPreview.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：hover

## 原始实现提示词

Create a React component called LetterHover using React + Tailwind CSS + Framer Motion. It renders a word (e.g. 'MotionVault', 32px, font-semibold, zinc-950) with each letter as an inline-block motion.span so transforms work. Track the hovered letter index in state (onMouseEnter per letter, reset to null on container onMouseLeave). The hovered letter springs to scale 1.4, y -8px, and a slight rotate of ±6deg alternating by letter index parity; letters exactly one position away get 15% of that same displacement (scale ~1.06, y ~-1.2px, rotate ~±0.9deg) for a rubber-band pull, and all other letters stay at rest. Use a spring transition with stiffness 500 and damping 15 on every letter so both the jump and the return bounce feel physical. Cursor pointer on the container, will-change-transform on letters, animate transform only for 60fps.
