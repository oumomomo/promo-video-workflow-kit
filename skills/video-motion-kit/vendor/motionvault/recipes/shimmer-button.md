# 微光按钮

一条柔和的光带周期性掠过深色按钮表面，辅以细腻的 1px 内高光环——克制而高级。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/button/ShimmerButton.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React component called ShimmerButton using React + Tailwind CSS + Framer Motion (Magic UI shimmer style). A dark zinc-950 pill button (rounded-full, white text 'Get Started', px-7 py-2.5) with overflow-hidden. Inside, an absolutely positioned 120px-wide motion.span band whose background is a linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent), slightly skewed (-12deg), sweeping from left to right (translateX -160px → 360px, 1.2s ease-in-out) and repeating every 3s (1.8s repeat delay). Add a subtle 1px inner highlight ring via inset box-shadow (inset 0 0 0 1px rgba(255,255,255,0.08) plus inset 0 1px 0 rgba(255,255,255,0.12)). Transform/opacity only — restrained and premium, not gaudy. Respect prefers-reduced-motion by disabling the band.
