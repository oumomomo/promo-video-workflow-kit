# 环形旋转文字

一行文字沿圆环缓慢旋转（12 秒一圈），悬停时像唱片机一样平滑加速到 4 倍速，离开缓缓减速——加速过程用 lerp 插值，绝不生硬。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/text/CircularTextPreview.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：hover

## 原始实现提示词

Create a React component called CircularText using React + Tailwind CSS. It renders a short phrase (e.g. 'MOTION VAULT · 灵感库 · ', repeated enough times to fill the circumference) along a perfect circle using an SVG <textPath> on a circular <path> (viewBox 200x200, radius 78, monospace 11.5px, letter-spacing 0.16em, uppercase, fill zinc-950), with a small center icon (arrow-down inside a white bordered circle) sitting in the middle. Drive the rotation with requestAnimationFrame writing transform: rotate() directly to a ref'd wrapper — 360deg per 12 seconds at rest. Track a target speed multiplier in a ref (1 normally, 4 while hovered via onMouseEnter/onMouseLeave) and exponentially lerp the current speed toward the target each frame (factor ~dt * 3.2) so acceleration and deceleration feel like a record player spooling up, never abrupt. Clamp dt to 50ms, keep the loop in a single useEffect with cancelAnimationFrame cleanup, add will-change-transform, and animate transform only for 60fps. Monochrome (zinc-950 on light background), cursor pointer, aria-label on the container.
