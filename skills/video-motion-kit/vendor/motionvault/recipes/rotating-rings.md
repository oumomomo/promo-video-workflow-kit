# 旋转圆环组

多个圆环以不同轴角和速度旋转，交错出陀螺仪般的秩序感。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/threeD/RotatingRings.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：move

## 原始实现提示词

Create a React Three Fiber gyroscope scene: five concentric torus rings
(radii 1.0 to 2.0, tube 0.015, white wireframe, opacity 0.5→0.9 from inner
to outer). Each ring has a random initial tilt (±0.6 rad on x/y) and spins
at a different speed (0.2-0.6 rad/s, alternating direction). The group
subtly tilts toward the mouse (±0.1 rad, lerped). Dark background.
