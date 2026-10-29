# 噪声波纹

多层正弦波纹缓慢交叠流动，像平静的水面反光（浅色版，适配白底页面）。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/background/NoiseWaves.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：move

## 原始实现提示词

Create a React noise-waves background on Canvas 2D over white: five
horizontal wave paths, each the sum of two sine layers (amplitude 12-28px,
wavelength 200-400px, speeds 0.2-0.5/s, distinct phases), stroked at 1.5px
in black at 6-14% opacity, spread vertically across the middle band. Waves
flow slowly sideways; the cursor's y-position subtly scales the middle
waves' amplitude (±30%). rAF loop, pause offscreen, resize-aware.
