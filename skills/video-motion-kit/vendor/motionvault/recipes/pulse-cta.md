# 呼吸光环

两圈柔和的光环从按钮边缘缓缓扩散又淡出，平静地把视线引向主行动按钮。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/button/PulseCTA.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React component called PulseCTA using React + Tailwind CSS + Framer Motion. A primary black pill button (bg-zinc-950, white text 'Start Free Trial', rounded-full, px-7 py-2.5) wrapped in a relative container. Behind the button, two absolutely positioned motion.span rings (inset-0, rounded-full, 1.5px zinc-400 border) continuously emanate outward from the button's edge: each animates scale 1 → 1.5 while fading opacity 0.6 → 0 over 2.2s ease-out, repeating infinitely; the second ring is delayed 1.1s so the pulses alternate evenly. Transform/opacity only for GPU-friendly animation. Calm, attention-guiding pulse. Respect prefers-reduced-motion by disabling the rings.
