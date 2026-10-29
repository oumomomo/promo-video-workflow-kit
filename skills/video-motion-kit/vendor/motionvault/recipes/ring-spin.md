# 渐变环

一圈由深到透明的渐变环匀速旋转——最顺滑的 spinner，没有接缝与顿挫。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/loader/RingSpin.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React component called RingSpin using React + Tailwind CSS + Framer Motion. A 40px circle (h-10 w-10 rounded-full) whose background is a conic-gradient(from 0deg, rgba(9,9,11,0) 0%, #09090B 100%) — fading from transparent into near-black. Mask it into a ring shape with a radial-gradient CSS mask (radial-gradient(farthest-side, transparent calc(100% - 4.5px), #000 calc(100% - 4px)), set both mask and WebkitMask) so only a ~4px stroke is visible. Rotate it 0 → 360deg over 0.8s, linear, infinite — perfectly smooth with no steps or seam. Respect prefers-reduced-motion by rendering the ring static.
