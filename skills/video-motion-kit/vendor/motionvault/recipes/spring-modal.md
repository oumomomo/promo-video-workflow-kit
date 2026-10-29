# 弹簧弹窗

弹窗带着明显的过冲弹簧蹦进来，还能用手指向下拖——拖过 100px 就松手坠落关闭。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/spring/SpringModal.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：click

## 原始实现提示词

Create a React component called SpringModal using React + Tailwind CSS + Framer Motion. A button '打开弹窗' opens a modal rendered inside a relative preview container (absolute positioning, NOT fixed — the backdrop covers the preview only). The backdrop fades in (opacity 0 → 1, 200ms, bg-zinc-950/20) and closes on click. The modal card (w-[280px], rounded-2xl, white bg, zinc-200 border, title + body text + a full-width dark action button + an ✕ close button) enters with an overshoot spring: initial scale 0.6 / y 40 / opacity 0 animating to scale 1 / y 0 / opacity 1 with type 'spring', stiffness 260, damping 17 — a visible bounce past the target. The card is draggable vertically (drag='y', dragConstraints bound to the preview container ref, dragElastic top 0.05 / bottom 0.4, cursor-grab); on drag end, if the y offset exceeds 100px dismiss it — the exit is a quick drop-down (y 120, opacity 0, 220ms easeIn). Wrap everything in AnimatePresence.
