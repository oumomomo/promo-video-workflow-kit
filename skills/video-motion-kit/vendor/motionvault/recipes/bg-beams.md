# 光束流动

五条细曲线路径自顶部垂落，光点沿路径周期流动，顶端淡入、底端淡出。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/background/BackgroundBeams.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React component called BackgroundBeams using React + Tailwind CSS + inline SVG with declarative SMIL (Aceternity Background Beams, restrained monochrome). A full-bleed SVG (viewBox 0 0 800 500, preserveAspectRatio "none", absolute inset-0) over a white base holds 5 gently S-curved paths dropping from the top edge to the bottom (e.g. M 90 -10 C 150 130, 40 300, 110 510), stroked 1px in zinc-200 (#E4E4E7) with vector-effect non-scaling-stroke. Along each path travels a short bright pulse — a 2.6px zinc-400 dot wrapped in a 9px rgba(161,161,170,0.12) halo — driven by animateMotion with an mpath reference, looping on staggered durations 4.2-6.9s with negative begin offsets so the phases never align. Pair each animateMotion with an opacity animate (values 0;1;1;0, keyTimes 0;0.12;0.85;1, same dur/begin) so pulses fade in at the top and out at the bottom. No JS, no rAF, no timers. Overlay a centered mock heading (zinc-900 title + mono caption, pointer-events-none) for readability.
