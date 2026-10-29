# 多步加载

四个步骤每 900ms 推进一格：当前行点亮、前面行描绘对勾，走到底停留一秒后重置循环。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/loader/MultiStepLoader.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React component called MultiStepLoader using React + Tailwind CSS + Framer Motion. Inside a 256px white card (rounded-xl, 1px zinc-200 border, p-4) render a vertical list of 4 steps — '校验数据' '建立连接' '同步资源' '完成'. A step counter state (0..4) advances every 900ms via setTimeout in useEffect, gated by an IntersectionObserver in-view flag (reset to 0 when scrolled out); after the last step hold 1000ms, then reset to 0 and loop forever. Each row shows a status indicator + label + right-aligned mono micro-label: pending = 8px zinc-300 dot, text zinc-400, 'wait'; active = 8px zinc-950 dot pulsing scale [1, 1.4, 1] / opacity [1, 0.55, 1] (0.9s infinite), text zinc-950 font-medium, 'running'; done = 20px zinc-950 filled circle popping in (scale 0.6→1) containing a white SVG check path ('M2 5.2l2 2L8 3') whose pathLength draws 0→1 over 300ms, text zinc-600, 'done'. Colors transition zinc-400 → zinc-950 over 300ms. Header row: mono uppercase 'LOADING SEQUENCE' + mono counter 'n/4'. Footer: a 2px zinc-100 track whose zinc-950 fill eases scaleX to step/4 (origin-left, 350ms easeOut). With prefers-reduced-motion render the all-done state statically.
