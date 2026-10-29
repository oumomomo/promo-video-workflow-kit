# 波浪平面

一个由点或细线构成的平面像海面一样起伏，极简而催眠。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/threeD/WavePlane.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React Three Fiber wave plane: an 80x80 grid of points spanning
12x12 units, camera at a 45deg elevated angle. Animate each point's z with
z = sin(x*0.8 + t) * cos(y*0.8 + t) * 0.4, t advancing at 0.8/s. Lerp point
color between zinc-700 and zinc-100 by wave height. Add a slow ±5deg
breathing rotation of the whole plane. Dark background, points material.
