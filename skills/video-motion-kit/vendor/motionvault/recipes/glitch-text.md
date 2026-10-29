# 故障艺术字

悬停瞬间文字撕裂成 RGB 重影——玫瑰红与天蓝两层残影左右错位，clip-path 切片以 steps() 硬切跳动，600ms 爆发后恢复干净字面。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/text/GlitchTextPreview.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：hover

## 原始实现提示词

Create a React component called GlitchText using React + Tailwind CSS with a component-scoped <style> block. It renders one word ('GLITCH', monospace, 40px, medium, uppercase, tracking 0.08em, zinc-950) as three stacked layers: the base glyph plus two absolutely-positioned aria-hidden copies (inset-0) colored rose #F43F5E and sky #38BDF8, both at opacity 0 at rest. On hover a state class enables a 600ms burst that runs exactly once per hover (CSS animations, 1 iteration, default fill so everything reverts clean afterward): the rose copy shifts -3px (jittering to -6px), the sky copy +3px (to +6px), both at 0.6 opacity; each copy's visibility is chopped into 3-4 horizontal clip-path inset() slices that jump discretely using animation-timing-function steps(1, end) across 5 keyframes (e.g. inset(8% 0 72% 0) → inset(58% 0 12% 0) → inset(24% 0 52% 0) → inset(78% 0 4% 0)), and the base glyph gets a subtle ±2px translate jitter on the same steps() timing. At 100% every layer returns to opacity 0 / translate 0 so off-burst text is perfectly clean. Re-hovering replays the burst. Transform and opacity only, will-change-transform, light background.
