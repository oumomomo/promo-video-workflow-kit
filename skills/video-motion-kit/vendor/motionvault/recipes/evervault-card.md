# 加密矩阵卡

满屏随机字符的矩阵中，鼠标周围的圆形区域被点亮成深色高亮并高速刷新，像一束扫描光扫过密文。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/card/EvervaultCard.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：move

## 原始实现提示词

Create a React component called EvervaultCard using React + Tailwind CSS + Framer Motion, recreating the Aceternity Evervault effect. Render a white card (340×220px, rounded-xl, 1px zinc-200 border, overflow hidden, cursor-crosshair) filled with a matrix of random glyphs (A–Z, 2–9, #$%&@*+=<>/ — 46 cols × 14 rows, JetBrains Mono 10px, 14px line-height, 2px tracking, rendered as a whitespace-pre <pre>). Render the matrix twice: a dim base layer (zinc-300) that slowly re-rolls every 2.6s, and a lit layer (zinc-950, font-medium) that re-rolls every 140ms. Track the pointer with onPointerMove into useMotionValue x/y (never useState in the pointer path) and build a mask with useMotionTemplate: radial-gradient(130px circle at x y, black 25%, transparent 100%) applied as maskImage/WebkitMaskImage on the lit layer via a motion.pre — so a circular region around the cursor lights up with freshly scrambled dark glyphs like a scanning spotlight. On pointer leave set both MotionValues to −400 so the lit region slides off. Center a small frosted pill chip (white/85, backdrop-blur, hairline border, mono 10px uppercase "ENCRYPTED") as the only static content.
