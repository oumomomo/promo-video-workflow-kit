# 边框光束

一道黑色光束沿按钮边框循环扫过——为克制的界面加一点克制的炫技。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/button/BorderBeam.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React component called BorderBeam using React + Tailwind CSS + Framer Motion. Wrap a black button (rounded-lg, bg-zinc-950, white text, px-6 py-2.5) in a relative overflow-hidden container with 1px padding — that padding is the visible border. Behind the button, place an absolutely positioned square motion.div (width 300% of the container, centered with translate -50%/-50%) whose background is conic-gradient(from 0deg, transparent 0deg, transparent 300deg, #09090B 340deg, #09090B 360deg) forming a short beam segment. Rotate it 0→360deg on a 3s linear infinite loop so the beam sweeps continuously around the button's border. The button sits above with a 7px radius and a hover state (bg-zinc-800). The beam color and duration should be easy to tweak via props.
