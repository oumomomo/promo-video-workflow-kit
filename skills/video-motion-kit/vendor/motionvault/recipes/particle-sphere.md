# 粒子球体

数千个粒子组成的球体缓缓自转，鼠标靠近时粒子被扰动推开。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/threeD/ParticleSphere.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：move

## 原始实现提示词

Create a React Three Fiber particle sphere: 4000 points sampled on a
Fibonacci sphere of radius 2, size 0.015, white at 0.7 opacity, rotating
slowly around Y (0.08 rad/s). When the mouse (raycast into the scene) comes
within 0.8 units, push nearby particles outward along their normals and let
them spring back over ~1s. Update positions in useFrame or via a custom
shader with a uMouse uniform. Dark background.
