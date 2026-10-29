# 扫光按钮

一道斜向高光周期性地扫过按钮表面，像被阳光掠过。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/button/ShineSweep.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React shine-sweep button: inside an overflow-hidden black button,
a diagonal (45deg) white gradient band (40% width, 0.25 opacity) sweeps
from left to right (translateX -150% → 150%, 0.8s ease-in-out) every 3.5s,
and once immediately on hover. Pseudo-element implementation, transform
only, no layout thrash.
