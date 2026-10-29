# 果冻按钮

点击瞬间按钮像布丁一样被压扁又弹回——横向拉伸时纵向收缩，体积守恒的果冻物理。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/spring/JellyButton.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：click

## 原始实现提示词

Create a React component called JellyButton using React + Tailwind CSS + Framer Motion. A chunky pill button (rounded-full, bg-zinc-950, white text '点我试试', px-10 py-4, font-semibold). On click, trigger an extreme squash-and-stretch jelly animation via useAnimationControls as two chained springs: first await controls.start({ scaleX: 1.3, scaleY: 0.75 }, { type: 'spring', stiffness: 400, damping: 10 }) to squash out fast with volume preservation, then controls.start({ scaleX: 1, scaleY: 1 }, { type: 'spring', stiffness: 300, damping: 8 }) so the low-damping settle overshoots and jiggles like pudding. Do NOT use a keyframed [1, …, 1] array with a spring transition — framer-motion's spring generator only reads the first and last keyframe, so identical endpoints silently produce no animation. Fully re-clickable — every click restarts the jiggle. Transform only, centered on a light preview.
