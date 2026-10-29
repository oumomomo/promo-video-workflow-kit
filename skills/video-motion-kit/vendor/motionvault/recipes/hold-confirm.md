# 长按确认

危险操作的防误触模式——按住 1.2 秒让填充从左扫到右才生效；中途松手，填充在 200ms 内无情回吐，绝不姑息。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/button/HoldConfirm.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：click

## 原始实现提示词

Create a React HoldConfirm button (danger-action pattern) using React + Tailwind CSS + Framer Motion. An outlined button (1px rose-600 border, rose-600 text, Trash2 icon + label '长按删除', w-40 h-11, rounded-lg, select-none). On pointerdown, a translucent rose fill (bg-rose-600/15, origin-left, transform scaleX bound to a MotionValue) sweeps left → right across the button over 1.2s, linear — progress MUST be driven by requestAnimationFrame, not a CSS animation, so early release works. Completing the hold flips the button to filled rose-600 with white text, a Check icon and '已删除' (spring scale pop), then it resets to idle after 1.5s. Releasing early (pointerup or pointerleave) cancels the hold and drains the fill back to 0 over 200ms — no partial credit. Cancel the rAF loop and timers on unmount, prevent the context menu, and use touch-action none so mobile holds aren't interrupted. Center on a light preview.
