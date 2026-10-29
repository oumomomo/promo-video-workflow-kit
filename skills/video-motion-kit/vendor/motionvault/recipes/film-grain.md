# 胶片颗粒

老电影质感：细密的颗粒噪点以 12fps 跳动闪烁，偶有竖直划痕与暗角呼吸——任何页面一秒变胶片。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/background/FilmGrain.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React component called FilmGrain using React + plain Canvas 2D (no extra libraries). A near-black canvas (#0C0C0E) fills its container (absolute inset-0, DPR-aware sizing via ResizeObserver, clamp DPR to 2). Pre-render 6 grain frames offscreen (144x144 tiles of random luminance noise, alpha 0.05-0.16 per speckle) and cycle them at 12fps via pattern fill over the whole canvas — the low frame rate is the charm, like projector judder. Add a slow-breathing vignette (radial gradient, edge alpha oscillating 0.32->0.44 over 7s), and sparse vertical scratches: 0-2 hairlines (rgba(255,255,255,0.05), 1px) that appear at a random x every 1.5-4s, jitter sideways ±2px per grain-frame, and vanish after 0.4-1.2s; every ~9s a 60ms dust flicker (small light blotches). Keep everything monochrome and subtle so foreground content stays readable. Pure rAF loop with time-based frame stepping; clean up the loop and ResizeObserver on unmount.
