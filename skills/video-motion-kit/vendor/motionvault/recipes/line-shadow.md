# 线影文字

72px 粗体 SHADOW 的“投影”由一片向下生长的 1px 细竖线构成，长度与透明度随时间正弦错落呼吸，像印刷版的错觉阴影。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/text/LineShadowPreview.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React component called LineShadowText using React + Tailwind CSS + Framer Motion. It renders 'SHADOW' at 72px, font-bold, tracking -0.02em, zinc-950, each glyph in a relative inline-block. Under every glyph render a fan of 12 hairline vertical lines (w-px, bg-zinc-950, flex row with 3px gap, absolutely positioned just below the baseline, centered on the glyph) wrapped in a mask-image linear-gradient(to bottom, black 35%, transparent 96%) so the fan fades out at its foot. Line heights vary from 34px at the edges to 56px in the middle of each fan (light-falloff profile). Every line is a motion.span with origin-top animating scaleY [0.25, 1, 0.25] and opacity [0.12, 0.65, 0.12] — duration 2.4s, ease-in-out, repeat Infinity, delay = charIndex * 0.16s + lineIndex * 0.06s — so the shadow grows downward and breathes in staggered waves, a print-plate illusion. transform (scaleY) and opacity only, will-change-transform, aria-label on the word, glyphs aria-hidden, light background.
