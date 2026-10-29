# 漂浮粒子场

大小不一的尘埃粒子缓缓上浮、明暗呼吸，安静的氛围背景。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/particle/ParticleDrift.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React ambient particle-drift background on Canvas 2D: 60 soft white
particles (radius 0.8-3px) float slowly upward (0.1-0.35 px/frame) with
horizontal sine sway (amplitude 10-25px, period 3-7s). Each particle
breathes in opacity (0.1-0.6) on its own phase (2-5s period). Wrap from top
edge back to bottom. Pure rAF loop, pause offscreen. Works as a page
background layer (absolute, inset-0, -z-10). Dark background.
