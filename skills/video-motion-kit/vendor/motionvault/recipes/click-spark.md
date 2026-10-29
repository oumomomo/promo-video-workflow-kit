# 点击火花

点击任意处迸发放射状火花：短线条四散飞出、受重力下坠、迅速淡出，zinc 单色点缀少量琥珀。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/particle/ClickSpark.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：click

## 原始实现提示词

Create a React component called ClickSpark using React + plain Canvas 2D (no extra libraries). A light (zinc-50) canvas fills its container (absolute inset-0, cursor pointer, DPR-aware sizing via ResizeObserver, clamp DPR to 2). On click, burst 8-12 spark streaks from the click point: directions evenly spread over 360deg with random jitter, initial speed 2.2-5.6 px/frame with a slight upward bias. Each spark is drawn as a short round-capped line segment (7-14px long, 1.2-2.1px wide) trailing behind its velocity vector. Colors are mostly zinc-950 #09090B with some zinc-500 #71717A, and roughly 1 in 4 sparks is amber #F59E0B. Sparks feel gravity 0.16 px/frame^2, air drag 0.985, live 480-800ms, fade linearly while their streak length shrinks to zero. Multiple rapid clicks must stack bursts. Show a centered hint text "点击任意位置" (12px zinc-400, pointer-events none). Clean up requestAnimationFrame, ResizeObserver and listeners on unmount.
