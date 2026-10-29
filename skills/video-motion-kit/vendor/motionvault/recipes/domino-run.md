# 滚动多米诺

滚动推倒九块多米诺：每块弹簧过冲地砸向下一块，连锁一路传到尽头，最后一块撞响铃铛，声波荡开，一声「叮」。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/scroll/DominoRun.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：scroll

## 原始实现提示词

Create a React component called DominoRun using React + Tailwind CSS + Framer Motion. Use the internal-scroll-container pattern (320px overflow-y viewport, thin custom scrollbar, progress hairline + fading scroll hint) with a 1000px track and a sticky 320px stage. Nine dominoes stand on a 1px zinc-200 baseline (bottom-16, px-4 stage): each is 14×64px, rounded-[3px], zinc-900 with a single white pip dot at center, spaced 30px apart starting at left 20px, z-index increasing left→right so each fallen domino lies on the next. Tipping: domino i maps scrollYProgress [0.05 + i·0.082, +0.075] → rotate 0 → 66° (transformOrigin '100% 100%', pivoting on its bottom-right edge), smoothed by useSpring (stiffness 420, damping 13) so it overshoots and wobbles as it slaps down; overlapping windows make the chain continuous. A live counter pill (top-left, mono uppercase, tabular-nums) reads 已倾倒 n / 9, derived via useMotionValueEvent (a domino counts fallen at 40% through its window; setState on change only). At the end of the run (62px past the last domino): a 36px circle button with a Bell icon — past progress 0.82 it turns amber (amber-50 bg, amber-500 icon) and swings rotate keyframes [-22,15,-9,5,0] over 900ms pivoting from its top, two expanding amber sound-ripple rings (scale 0.5→1.9 fade, 180ms apart), and a '叮!' zinc-950 pill pops above it with a spring. Scrolling back below 0.5 resets the bell. Bottom-left phase chip: 滚动 · 推倒第一块 → 连锁反应进行中… → 势不可挡 → 全部倒下 — 铃声为证.
