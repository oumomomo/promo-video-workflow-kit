# 点击波纹

Material 风格——点击处荡开一圈涟漪，最直接的触碰反馈。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/button/Ripple.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：click

## 原始实现提示词

Create a React ripple button (Material style): on pointerdown, spawn a
white circle (0.35 opacity) at the click coordinates inside the overflow-
hidden button, animate it to scale 3 and fade out over 0.6s ease-out, then
remove it from the DOM. Support multiple concurrent ripples and keyboard
activation (Enter/Space) rippling from center. Track click position with
getBoundingClientRect.
