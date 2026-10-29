# 自动换牌卡堆

三张卡片循环换牌：每 3 秒最前面的卡先下沉 60px 并微微淡出，再滑到卡堆最后，其余卡片依次向前递补，安静而持续。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/card/CardSwap.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React component called CardSwap using React + Tailwind CSS + Framer Motion. Render three stacked cards (320×128px, rounded-xl, 1px zinc-200 border, subtle gradient faces with a small accent bar, mono uppercase label, title, and two skeleton lines) absolutely positioned in a fixed wrapper. Drive the cycle with a reordered id array in state: every 3 seconds a setInterval (only running while the component is in view via IntersectionObserver) moves the front id to the back. Each card is a motion.div keyed by id with initial={false}, animating to its slot values — front: y 0, scale 1, opacity 1, zIndex 30; middle: y 14, scale 0.95, opacity 0.85, zIndex 20; back: y 28, scale 0.9, opacity 0.7, zIndex 10. Track the previous order in a ref; the card moving from front to back animates with keyframes instead — y [0, 60, 28], scale [1, 0.97, 0.9], opacity [1, 0.55, 0.7], zIndex [30, 30, 10] over 700ms with times [0, 0.45, 1] — so it drops down 60px and fades slightly before sliding behind the stack, while the other cards step forward with a 500ms ease [0.16,1,0.3,1] tween.
