# 卡片换位

三张错位微旋的卡片叠放：每 4 秒顶卡向前上方抽出并淡化，从后方落回牌堆最底，其余卡片前移补位，如循环洗牌。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/layout/CardSwapCycle.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React component called CardSwapCycle using React + Tailwind CSS + Framer Motion. Render three cards (320×168px, rounded-xl, hairline zinc-950/10 border, soft shadow, muted pastel gradient faces — sand/sky/sage — each with a mono uppercase deck tag, a semibold Chinese title and two rounded skeleton bars) absolutely stacked in a fixed 320×230px wrapper with slight offsets and rotations: front y 0 / rotate −2.5deg / scale 1 / zIndex 30, middle y 15 / rotate 1.8deg / scale 0.95 / opacity 0.92 / zIndex 20, back y 30 / rotate −1.2deg / scale 0.9 / opacity 0.75 / zIndex 10. Drive the cycle with an order array in useState: a setInterval (4000ms, only running while in view via IntersectionObserver) moves the front id to the back. Each card is a motion.div keyed by id with initial={false}; the card moving from front to back animates with keyframes — y [0, −78, −78, 30], rotate [−2.5, 2, 2, −1.2], scale [1, 1.04, 1.04, 0.9], opacity [1, 0, 0, 0.75], zIndex [30, 40, 5, 10] over 850ms with times [0, 0.38, 0.6, 1] — so it draws out forward-up, fades, and drops in from behind the stack, while the remaining cards step forward with a 550ms cubic-bezier(0.22, 1, 0.36, 1) tween. Track the previous order in a ref to identify the card that must take the keyframe path; all others tween to their new slot.
