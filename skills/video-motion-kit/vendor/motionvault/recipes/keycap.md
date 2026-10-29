# 立体按键卡

一颗巨大的机械键盘键帽：按下时顶面真实下沉 8px、侧沿随之收短、投影变软，松手后 Q 弹回位，越按越上瘾。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/card/KeycapCard.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：click

## 原始实现提示词

Create a React component called KeycapCard using React + Tailwind CSS + Framer Motion. Render a big mechanical keycap (128×128px) centered on the preview: a darker zinc-300 side/bottom layer (rounded-2xl, same size, translated 8px down so it peeks out as an extruded lip) behind a zinc-100 top face (rounded-2xl, 1px zinc-200 border) carrying a big mono letter 'K'. The top face holds an inset dished surface (an inner rounded-xl zinc-50 panel with shadow-[inset_0_3px_10px_rgba(0,0,0,0.10)] for a subtle concave key dish). Drive the press with a useMotionValue y smoothed by useSpring (stiffness 500, damping 25): on pointerdown set y to 8 so the top face physically translates down 8px and covers the side lip (the extrusion visually shrinks to zero); on pointerup / pointerleave / pointercancel set y back to 0. Derive the drop shadow from the same spring via useTransform — a soft 14px blur shadow at rest collapsing to a tight 2px contact shadow when fully depressed — for a satisfying click feel. Add a tiny mono counter below ('×N') that increments per press. Transform and opacity only, no setState in pointermove.
