# 光束流动

一条 S 形发卡弯轨道上，高亮光斑带着 3 个渐隐拖尾点循环流动——getPointAtLength 驱动，丝滑无缝。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/svg/BeamPathPreview.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React component called BeamPath using React + Tailwind CSS. It renders a 300x160 viewBox SVG containing a dim S-curve rail with a hairpin feel: path 'M 24 120 C 90 120 90 40 150 40 C 210 40 210 120 276 120', stroke #E4E4E7 (zinc-200), strokeWidth 1.5, round line cap, no fill, plus two small terminal dots (r 2.5, zinc-300) at both ends. A bright head dot (r 3.5, fill #09090B zinc-950) travels the rail in a 2.4s seamless loop, trailed by 3 ghost dots (r 3 / 2.5 / 2, opacity 0.32 / 0.18 / 0.09) sitting 16 / 32 / 48 path-units behind the head. Drive the motion with requestAnimationFrame: keep a ref to the rail path, call getTotalLength() once, and each frame compute t = ((now - start) % 2400) / 2400, then position every dot with path.getPointAtLength wrapped modulo the total length so the trail never jumps at the seam — write cx/cy via setAttribute directly on ref'd circles (no React state, 60fps). Gate the loop with an IntersectionObserver so it pauses off-screen and cancelAnimationFrame on cleanup. Center the svg (max-width ~360px) on a light background, monochrome zinc only, container aria-label.
