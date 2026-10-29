# 彗星尾迹卡

深色卡面上三颗小彗星错峰划过：亮头拖着渐隐的长尾，沿不同角度周期性掠过，周而复始。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/card/CometCard.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React component called CometCard using React + Tailwind CSS, in the spirit of Aceternity's Comet Card. Render a dark card (320×192px, zinc-900, rounded-xl, 1px zinc-800 border, overflow hidden) with minimal white content (mono uppercase label, title, two-line muted description). Three comets periodically sweep the card at different angles: each comet lives in an absolutely positioned full-width lane div (at ~22% / 50% / 74% from the top, rotated -24deg / -34deg / -18deg) containing a comet span — a fading tail (width 70–110px, height 1.5px, rounded-full, background linear-gradient(90deg, transparent, rgba(244,244,245,0.35) 55%, rgba(244,244,245,0.95))) with a bright head (5px zinc-100 circle, soft white glow box-shadow) anchored at its leading end. Drive all motion with one CSS keyframes loop (translateX -120px → card width +40px, opacity 0 → 1 by 10%, hold, fade to 0 by 100%) and stagger the three comets via inline animation-duration (4s / 5.5s / 7s) and animation-delay (0s / 1.6s / 3.2s) so they never sync up. transform + opacity only, will-change transform, paused with animation-play-state when the card scrolls out of view (IntersectionObserver). Isolate the comet field in a memoized micro-component.
