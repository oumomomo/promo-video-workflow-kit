# 星空穿梭

数千颗星星迎面飞来，穿越深空——点击可加速跃迁。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/threeD/Starfield.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：click

## 原始实现提示词

Create a React Three Fiber starfield: 3000 stars distributed in a 60-unit
deep tunnel flying toward the camera along -z at 6 units/s, wrapping back
to the far end after passing the camera. Point size attenuates with
distance, white stars, camera fov 70, black background. On click, lerp
speed to 30 u/s over 3s (stars stretch into streaks via elongated
geometry or shader), then ease back over 2s.
