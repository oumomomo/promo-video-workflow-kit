# 逐位滑换数字

四位计数器的每一位都是一条独立的数字卷轴——点击 +1/+10 时老数字上滑出、新数字滑入，个位先动、逐位错峰 40ms 回稳。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/spring/SlidingNumber.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：click

## 原始实现提示词

Create a React component called SlidingNumber using React + Tailwind CSS + Framer Motion. A 4-digit counter in a mono font (font-mono, text-5xl, 48px, zinc-950) with leading-zero padding. Each digit is its own column: a 1em-tall window (overflow-hidden, width 0.62em) containing a vertical stack of digits 0-9 (each span exactly 1em tall, leading-none). To change a digit, animate the column's y to -digit em with Framer Motion (initial={false}) using a spring transition (type: 'spring', stiffness 300, damping 24) so the old digit slides up out and the new one slides up in, settling with a soft bounce. Stagger the digits by 40ms from the ones place outward (delay = (length - 1 - index) * 0.04) for an odometer-carry feel. Below the counter, two buttons: a dark '+1' (bg-zinc-950, white text) and an outlined '+10', both with active:scale-95 press feedback. Transform-only animation, centered on a light preview.
