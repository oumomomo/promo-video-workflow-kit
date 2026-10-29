# 星光文字

标题周围持续生成细小的四角星光，缩放旋转着闪现再淡出，像灵感在字句间发光。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/text/SparklesTextPreview.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React component called SparklesText using React + Tailwind CSS + Framer Motion. It renders a large headline (e.g. 40px, font-semibold, zinc-950) inside a relative inline-block wrapper, and continuously spawns tiny four-point star sparkles at random positions around and above the glyphs (x -6% to 106%, y -45% to 125% of the text box, sizes 10-22px). Each sparkle is a pure SVG 4-point star path (M12 0c.85 6.5 5.5 11.15 12 12-6.5.85-11.15 5.5-12 12-.85-6.5-5.5-11.15-12-12C6.5 11.15 11.15 6.5 12 0Z), colored warm amber #E8B04B with ~25% of sparkles in zinc-400 for variety. Spawn one sparkle every ~170ms via setInterval, cap concurrent sparkles at 12, and give each a full lifecycle of 0.8-1.5s: scale 0→1.15→1 with a rotate from -45deg offset toward its random base rotation, a mid-life twinkle (opacity dips to ~0.55 and back), then scale 0 + fade + extra 60deg rotation on exit. Wrap the sparkle list in AnimatePresence so removals animate out; remove each sparkle from state with a setTimeout matching its duration, and clean up all timers on unmount. Sparkles are pointer-events-none and aria-hidden; keep the headline itself accessible via aria-label. Animate transform and opacity only for 60fps.
