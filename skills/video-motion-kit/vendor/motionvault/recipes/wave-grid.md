# 波浪方块阵

22×22 的哑光方块矩阵随径向正弦波起伏，涟漪中心跟随鼠标移动，安静而催眠。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/threeD/WaveGrid.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：move

## 原始实现提示词

Create a React component with React Three Fiber: a 22x22 grid of thin
matte boxes (0.32 x 0.32 footprint, zinc-800, spacing 0.44) on a #FAFAFA
canvas, heights driven by a radial sine wave h = 0.15 + (sin(dist - t*2.2)
+ 1) * 0.5 * 1.1 where dist is the distance from a ripple center. Raycast
the pointer onto the grid plane and lerp the ripple center toward the hit
point at 0.08 per frame; ease back to the origin on leave. Render with a
single instancedMesh, lerping instance color from zinc-800 to zinc-200 by
wave height so crests read lighter — keep it strictly monochrome. Camera:
45deg elevated view, plus a slow breathing rotation of ±3deg. Ambient 0.7 +
one directional light, no shadows.
