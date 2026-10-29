# 三点跳跃

三颗小圆点依次跳起又落下——经典打字指示器，节奏调得刚刚好。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/loader/DotsBounce.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React component called DotsBounce using React + Tailwind CSS + Framer Motion. Three 8px round dots (h-2 w-2 rounded-full bg-zinc-800) in a horizontal row with an 8px gap, centered in the container. Each dot bounces vertically — y keyframes [0, -10, 0] over 600ms with easeInOut, repeating infinitely — with a 150ms stagger delay between dots (delay = index * 0.15) so they jump in sequence like a typing indicator. Transform only. Respect prefers-reduced-motion by rendering the dots static.
