# 文字漩涡

Canvas 铺满 MOTION 字符网格，光标所在处形成漩涡——字符绕光标切向偏移并旋转、随距离衰减，离开后弹簧归位；近处字符由 zinc-400 转 zinc-950。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/text/VortexTextPreview.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：move

## 原始实现提示词

Create a React component called VortexText using React + Tailwind CSS + Canvas 2D. Fill the preview with a grid (62x46px cells) tiled with the word 'MOTION' (cell glyph = WORD[(row * cols + col) % 6], 13px JetBrains Mono 500, centered). Each frame (requestAnimationFrame gated by an IntersectionObserver, cancelAnimationFrame + ResizeObserver cleanup, DPR capped at 2, canvas sized via inline style absolute inset-0 100%x100%): compute each cell's distance to the cursor (pointermove on the canvas, pointerleave parks it at -9999); inside a 170px radius apply a smoothstep falloff s = f*f*(3-2*f) and push the glyph TANGENTIALLY around the cursor — offset = perpendicular(-dy, dx)/d * 24px * s — plus rotate up to 60deg * s. Targets spring toward zero when the cursor leaves (state += (target - state) * 0.14 per frame), so glyphs swirl and then settle back onto the grid. Color lerps zinc-400 (#A1A1AA) → zinc-950 (#09090B) by the same springed influence. Draw with ctx.save/translate/rotate/fillText/restore; no React state anywhere, cursor-crosshair, light background, container aria-label.
