# 线框几何雕塑

二十面体、圆环、八面体三层嵌套线框以不同轴速缓慢旋转，整体轻轻呼吸缩放——极简雕塑感。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/threeD/WireframeForms.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React component with React Three Fiber: a minimal wireframe
sculpture on a #FAFAFA canvas. Three nested wireframe solids — an outer
icosahedron (radius 1.55, zinc-400 #A1A1AA, opacity 0.75), a middle torus
(radius 1.02, tube 0.34, zinc-300 #D4D4D8, opacity 0.55, tilted ~65deg)
and an inner octahedron (radius 0.6, zinc-500 #71717A, opacity 0.9) — all
meshBasicMaterial wireframe, no lights. Each solid rotates on its own axes
at different slow speeds (0.1-0.32 rad/s, mixed directions). The parent
group breathes with scale = 1 + sin(t * 0.6) * 0.04 and drifts around y at
0.06 rad/s. Camera at [0, 0.4, 5], fov 42. Strictly monochrome, gallery-
quiet mood.
