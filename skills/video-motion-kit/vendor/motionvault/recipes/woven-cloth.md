# 织物波浪

48×48 顶点的细线框平面做交错正弦波浪，经纬相位交错起伏，像一块在风里微微抖动的布。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/threeD/WovenCloth.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React component with React Three Fiber: a woven-cloth wave on a
#FAFAFA canvas. A PlaneGeometry(6.4, 4.2, 48, 48) rendered as a single
meshBasicMaterial wireframe (zinc-400 #A1A1AA, opacity 0.8, no lights). Cache
the base positions once, then in useFrame rewrite each vertex z as
z = sin(x*1.1 + t*1.2)*0.26 + cos(y*1.5 + t*0.9)*0.2 + weave, where weave =
((ix+iy)%2===0 ? 1 : -1) * 0.07 * sin(t*1.7 + x*2.3 + y*1.1) — the
alternating warp/weft phase makes it read as fabric rather than a water
surface; set position.needsUpdate each frame. Tilt the group -0.95 rad on x
and add a slow rotation.z sway (±0.04 rad, sin(t*0.18)). Camera at
[0, 1.4, 4.3], fov 45. Strictly monochrome, quiet gallery mood.
