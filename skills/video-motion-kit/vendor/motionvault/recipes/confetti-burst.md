# 彩带爆发

点击瞬间从指尖炸开一把彩带与纸屑，庆祝专用。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/particle/ConfettiBurst.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：click

## 原始实现提示词

Create a React confetti-burst component on Canvas 2D: on click, explode
80-120 confetti pieces from the click point — colored rectangles (palette
#F43F5E #F59E0B #10B981 #3B82F6 #8B5CF6) plus round dots — with an upward
fan of initial velocities (3-9 px/frame, ±50deg), gravity 0.15, air drag
0.98. Rectangles tumble by oscillating scaleX (fake 3D flip). Fade out
before landing and clear the canvas after ~1.2s. Expose an onCelebrate
callback. No external libraries.
