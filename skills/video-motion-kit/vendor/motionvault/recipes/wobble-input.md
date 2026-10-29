# 抖动输入框

登录失败的经典反馈：整行左右抖动、边框闪红、错误提示从上方滑下——聚焦输入框即复位。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/spring/WobbleInput.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：click

## 原始实现提示词

Create a React component called WobbleInput using React + Tailwind CSS + Framer Motion. A login-ish row: a password input (h-10 w-52, rounded-lg, 1px zinc-300 border, placeholder '输入密码') next to a dark '登录' button (bg-zinc-950, white text). Clicking 登录 with any input runs the classic error shake on the whole row via useAnimationControls: x keyframes [0, -10, 10, -6, 6, -2, 0] over 400ms easeInOut. Simultaneously the input border flashes rose-500 for 800ms (state + setTimeout clearing it, transition-colors duration-300), and a small hint '密码错误，再试一次' (12px, text-rose-500) slides down below the row inside an overflow-hidden container (y -8 → 0, opacity 0 → 1, spring stiffness 400 damping 22, wrapped in AnimatePresence). Focusing the input again resets everything — border back to zinc-300, hint exits.
