# 粒子文字

文字由上千个粒子拼成，鼠标划过时粒子四散逃开再归位——交互感最强的一个。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/particle/ParticleText.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：move

## 原始实现提示词

Create a React particle-text component on Canvas 2D. Render a word
(e.g. "MOTION", 120px bold) to an offscreen canvas, sample pixels to get
~1500 target points. Particles start at random positions and spring toward
their targets (attraction 0.06, damping 0.86). Within 60px of the cursor,
apply a repulsion force (up to 8, distance-falloff) so particles scatter,
then spring back. White 1.2px dots on a dark background. rAF loop, pause
offscreen, rebuild on resize.
