# 词间形变

两个 64px 粗体词通过 blur 12px→0 + 缩放交叉溶解互相转化，1.8 秒一周期无缝循环，词宽不同也绝对居中、毫无跳动。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/text/MorphingTextPreview.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React component called MorphingText using React + Tailwind CSS + Framer Motion. It cycles between two bold words ('灵感' ⇄ '动效', 64px, font-bold, tracking -0.02em, zinc-950) every 1.8s on a setInterval gated by an IntersectionObserver (pause off-screen, clean up on unmount). Both words are absolutely centered inside a fixed-size relative wrapper (e.g. 260x104px flex center) so their different widths never cause layout shift. Wrap the keyed motion.span in AnimatePresence initial={false} and cross-dissolve: incoming word animates from { opacity: 0, scale: 1.18, filter: 'blur(12px)' } to { opacity: 1, scale: 1, filter: 'blur(0px)' }, outgoing to { opacity: 0, scale: 0.85, filter: 'blur(12px)' } — duration 1.1s, ease [0.16, 1, 0.3, 1], so the dissolve finishes well inside the 1.8s cycle for a seamless, never-idle loop. whitespace-nowrap, will-change-transform, wrapper carries an aria-label of the current word; light background.
