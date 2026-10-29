# 逐行揭示

段落在进入视口时逐行从遮罩中滑出，500ms 缓出、行间错峰 120ms，干净利落的编辑排版感。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/text/LineRevealPreview.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React component called LineReveal using React + Tailwind CSS + Framer Motion. It renders a 3-4 line paragraph (15px, zinc-700, generous ~2x line-height) where every line is wrapped in its own overflow-hidden block-level mask. Each line's inner span animates with whileInView from { y: '100%', opacity: 0 } to { y: '0%', opacity: 1 } — duration 500ms, ease-out, with a 120ms stagger via per-line delay. Use viewport={{ once: true, amount: 0.6 }} so the reveal triggers crisply the first time the paragraph scrolls into view and never replays. The mask keeps each line fully hidden until its turn, producing an editorial, gallery-quality reveal. Animate transform and opacity only; keep the text selectable.
