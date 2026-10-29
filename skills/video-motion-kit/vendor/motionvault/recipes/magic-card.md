# 光晕边界卡

一圈低饱和的径向光晕贴着卡片边框内侧游走，随鼠标位置移动，像光把边框从里面照亮。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/card/MagicCard.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：move

## 原始实现提示词

Create a React component called MagicCard using React + Tailwind CSS, recreating the Magic UI Magic Card. Render a white card (320×192px, rounded-xl) with minimal content (mono uppercase label, semibold title, two-line muted description). Build the glowing border with zero React state: wrap the card in an outer shell div with p-px (1px padding paints the border ring) whose background is two stacked layers — radial-gradient(240px circle at var(--mouse-x) var(--mouse-y), rgba(161,161,170,0.55), transparent 70%) over a solid #E4E4E7 base — so the border brightens in a soft zinc-400 halo around the cursor. Inside, the content div (rounded-[11px], white bg) carries a matching inner wash layer: radial-gradient(280px circle at the same CSS vars, rgba(161,161,170,0.14), transparent 65%), absolutely positioned and pointer-events-none — light appears to graze the inside of the frame. Track the pointer with onPointerMove on the shell and update it via el.style.setProperty('--mouse-x', px) / '--mouse-y' (coordinates relative to the shell's bounding rect); the vars inherit into both gradient layers. Default the vars to center-top so the card looks calm before first hover. No useState, no re-renders — pure CSS custom properties.
