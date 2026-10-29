# 曲线跑马灯

FIND INSPIRATION · MOTION VAULT 沿一条下弯弧线无限滚动，18px mono，弧线两端以渐变遮罩淡出，安静而有仪式感。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/text/CurvedLoopPreview.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React component called CurvedLoop using React + Tailwind CSS + SVG textPath. In a 640x160 viewBox define a shallow downward arc path 'M -60 34 Q 320 132 700 34' (fill none, unique id via useId). Render the phrase 'FIND INSPIRATION · MOTION VAULT · ' repeated 5 times inside a textPath (18px, JetBrains Mono, letterSpacing 0.06em, fill #09090B) plus a hidden single-unit text ruler. Measure the unit width once with getComputedTextLength (re-measure after document.fonts.ready), then run a requestAnimationFrame loop gated by an IntersectionObserver (cancelAnimationFrame on cleanup): offset = (offset + 55px * dt) % unit, writing startOffset = -offset directly on the textPath element via setAttribute — zero React state; the repeat count guarantees the text covers the path through the whole [-unit, 0] offset range so the wrap is seamless. Overlay two pointer-events-none gradient fades (w-20, from-zinc-50 to transparent) at the left and right ends of the arc. dt clamped to 50ms, svg carries an aria-label of the phrase, light background.
