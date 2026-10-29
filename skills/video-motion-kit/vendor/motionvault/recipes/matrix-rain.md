# 字符雨

极细的片假名与数字缓缓落下，白色字头拖着渐渐隐去的灰色残影——只是矩阵的一声耳语。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/background/MatrixRain.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React component called MatrixRain using React + plain Canvas 2D (no extra libraries) over a zinc-950 base. An elegant, RESTRAINED matrix rain: columns of tiny 10px monospace glyphs (half-width katakana + digits, 14px column width, 12px row height). Each frame, fill the canvas with translucent black rgba(9,9,11,0.08) so old glyphs fade into trails. Active columns advance their head at only 1.5-3 rows per second (delta-time based), drawing the head glyph in soft white at 80% opacity and the glyph one row behind in zinc-500; only ~60% of columns are ever active, and finished columns respawn at a random negative offset with a fresh random speed. Draw a glyph only when the head crosses into a new row so the fall stays slow and crisp — a whisper of the matrix, not a seizure. Canvas fills its container (absolute inset-0, DPR-aware sizing via ResizeObserver, clamp DPR to 2); clean up the rAF loop and observer on unmount.
