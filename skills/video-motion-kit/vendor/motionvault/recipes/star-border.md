# 星光绕边

一颗带着短拖尾的小星光沿深色按钮的圆角轮廓循环巡游，悬停时按钮轻轻抬升。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/button/StarBorder.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：hover

## 原始实现提示词

Create a React component called StarBorder using React + Tailwind CSS + CSS Motion Path (offset-path, no canvas). A dark pill button (h-11, rounded-full, bg-zinc-950, white text, inset 1px white/14 ring). Overlay a small traveling star: a 36x8px span holding a short comet trail (linear-gradient 90deg from transparent through white/45 to white/95) with a 5px glowing white head (box-shadow 0 0 8px 2px rgba(255,255,255,0.75)) at its leading edge. Measure the button with a ResizeObserver and build a rounded-rect perimeter path string — M r 0 H w-r A r r 0 0 1 w-r h H r A r r 0 0 1 r 0 Z with r = height/2 — then set it as the span's offset-path via inline style, offset-rotate: auto so the head always points forward, and animate offset-distance 0% to 100% on a 4.5s linear infinite keyframes loop. On hover the button lifts (-translate-y-0.5) with a soft dark drop shadow over 300ms. Wrap the star in a memoized micro-component; honor prefers-reduced-motion.
