# 多股线浪

六条水平贝塞尔细线的控制点随时间正弦起伏，相位错落编织成一条缓慢流动的缎带，中间一条 zinc-950 主线领航。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/svg/StrandsPreview.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React component called Strands using React + Tailwind CSS (no Framer Motion needed — drive it with requestAnimationFrame). It renders a 320x180 viewBox SVG with 6 horizontal cubic-bezier strands. Strand i sits at baseY = 44 + i*18 and its path is 'M 6 baseY C 92 c1 228 c2 314 baseY' where the control points ride phase-offset sine waves: c1 = baseY + 13 * sin(t*1.25 + i*0.75), c2 = baseY + 13 * sin(t*1.25 + i*0.75 + PI*0.66). Keep an array of path refs; each rAF frame recompute every strand's d and write it via setAttribute directly (round to 2 decimals, zero React state, 60fps). Strand index 2 is the lead — stroke #09090B strokeWidth 1.6 full opacity; the other five are #A1A1AA (zinc-400) at 1px and 0.75 opacity. All round line caps, no fill. Gate the loop with an IntersectionObserver-based useInView hook so it only runs while visible; cancelAnimationFrame on cleanup. Center the svg (max-width ~380px) on a light background, container aria-label.
