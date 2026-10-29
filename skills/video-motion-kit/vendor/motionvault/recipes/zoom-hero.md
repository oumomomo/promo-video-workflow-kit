# 滚动缩放封面

封面大图从 1.25 倍缓缓回落至原始尺寸，标题淡出、副标题浮现——电影开场的呼吸感。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/scroll/ZoomHero.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：scroll

## 原始实现提示词

Create a React component called ZoomHero using React + Tailwind CSS + Framer Motion. All scrolling happens inside an internal scroll container (320px tall, overflow-y auto, overscroll-contain, thin 4px custom scrollbar) — never hijack page scroll. Inside it place a 2.5×-tall track (800px) with a sticky full-viewport panel. The panel holds a CSS-only landscape: a muted sky gradient (zinc/sage tones), a soft radial sun, and three mountain-silhouette layers drawn with clip-path polygons (light sage in back to deep zinc-green in front) plus a white mist gradient at the bottom. Drive useScroll({ container }) and scrub the landscape's scale from 1.25 to 1 via useTransform over scrollYProgress [0,1]. Overlay a centered title (small mono uppercase label + 2xl semibold Chinese title) that fades out and drifts -24px over progress [0,0.4], and a subtitle that fades in and rises 16px over [0.55,0.9]. Add a sticky 2px scroll-progress hairline at the top of the scroller and a "向下滚动" hint pill that fades out once progress passes 0.06. Transform/opacity only, 60fps.
