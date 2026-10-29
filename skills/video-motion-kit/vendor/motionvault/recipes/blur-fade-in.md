# 模糊浮现

文字逐词（或逐字）从模糊中浮现——opacity 0→1、blur 8px→0、轻微上移，词间错峰 120ms，适合标题与开场文案。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/text/BlurFadeInPreview.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React component called BlurFadeIn using React + Tailwind CSS + Framer Motion. It receives a `text` prop and renders it split into units: split by words when the text contains spaces, otherwise split per character (good for Chinese). Each unit is an inline-block motion.span animated from { opacity: 0, filter: 'blur(8px)', y: 10 } to { opacity: 1, filter: 'blur(0px)', y: 0 } with duration 0.7s, ease [0.16, 1, 0.3, 1], and a 0.12s stagger between units (configurable via `stagger` prop, plus a `delay` prop for the first unit). Support a `loop` prop that remounts the units on an interval (default ~4.2s) so the effect replays continuously. Keep the text selectable/accessible via an aria-label on the wrapper.
