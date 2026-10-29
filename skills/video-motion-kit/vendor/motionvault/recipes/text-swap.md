# 文字滑换

悬停时文字向上滑出、新文案从下方滑入——干脆利落的排版微交互。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/button/TextSwap.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：hover

## 原始实现提示词

Create a React text-swap button: an outlined button (1px zinc-950 border, rounded-lg, black text) whose label area is a fixed-height (h-5) overflow-hidden container holding a vertical stack of two labels — default 'Learn More' on top and 'Free Trial →' below. On hover, the stack translates up by 50% so the first label slides up and out while the second slides up in from below; 280ms with cubic-bezier(0.22,1,0.36,1) easing; reverses smoothly on mouse leave. Pure CSS transition with Tailwind group-hover, transform only.
