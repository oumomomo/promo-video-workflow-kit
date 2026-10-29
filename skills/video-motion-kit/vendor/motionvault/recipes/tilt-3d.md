# 滚动摊平

一张"应用截图"卡从 rotateX 24° 的俯瞰姿态随滚动缓缓摊平到正视，上方标题同时上移淡出——产品发布页的经典开场。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/scroll/Tilt3D.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：scroll

## 原始实现提示词

Create a React component called Tilt3D using React + Tailwind CSS + Framer Motion. Use the internal-scroll-container pattern: a 320px overflow-y auto viewport (overscroll-contain, thin custom scrollbar, never page scroll) with a 680px track and a sticky full-viewport centered stage. Above the card, a title block (mono uppercase 'PRODUCT LAUNCH' caption + semibold Chinese title) drifts y 0 → -44 and fades opacity 1 → 0 over progress [0, 0.35]. Below it, wrap a 280px mock app screenshot card in a div with style perspective 900px; the card itself is a motion.div with transformStyle preserve-3d whose rotateX maps scrollYProgress [0.08, 0.6] → [24, 0] degrees, scale [0.88, 1] and y [24, 0] — it starts tilted back like a product-launch hero and flattens to a straight-on view as you scroll. The screenshot is pure CSS: a window chrome bar (zinc-50, three zinc-300 dots, a zinc-200 address pill), then a flex body — a 56px sidebar (zinc-50, stacked bars, one zinc-300 active) and a main pane with a zinc-800 title bar, two zinc-200 text bars and three small gradient thumbnails (zinc-100 → zinc-300). Rounded-xl, 1px zinc-200 border, soft shadow-xl. All useTransform ranges strictly increasing inside [0,1]; transform/opacity only. Top progress hairline + fading "向下滚动" hint included.
