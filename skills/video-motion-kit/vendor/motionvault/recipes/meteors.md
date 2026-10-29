# 流星雨

深邃夜空里流星斜向划过，拖着渐隐的光尾；偶尔有一颗更大更亮的火流星。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/particle/Meteors.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React component called Meteors using React + plain Canvas 2D (no extra libraries). A canvas fills its container (absolute inset-0, DPR-aware sizing via ResizeObserver, clamp DPR to 2) over a zinc-950 dark sky. Paint 40 tiny static stars (0.5-1.4px white dots, opacity 0.15-0.6) as a backdrop. Meteors spawn at staggered random intervals (every 300-900ms, max 8 alive) at a random x along the top (y slightly above the canvas) and travel diagonally about 35deg from vertical at 4-8 px/frame. Each meteor is a glowing 2px white head dot (shadowBlur 8) plus a ~120px tail drawn as a linear gradient stroke fading from rgba(255,255,255,0.6) to transparent opposite the travel direction. Roughly 1 in 5 meteors is larger and brighter (2.6px head, ~170px tail, higher speed). Remove meteors once fully offscreen. Clean up requestAnimationFrame and the ResizeObserver on unmount.
