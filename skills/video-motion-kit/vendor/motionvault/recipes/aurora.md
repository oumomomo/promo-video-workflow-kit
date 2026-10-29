# 极光

紫、蓝、绿三团柔和的径向渐变在深色底上缓慢流动，像安静的北极光。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/background/Aurora.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React component called Aurora using React + Tailwind CSS + Framer Motion. A full-bleed absolutely positioned container with a deep navy background (#0B1020) and overflow-hidden. Inside, render 3 large blurred blobs as motion.divs: each is a rounded-full div sized ~50–60% of the container, background radial-gradient(circle, color 0%, transparent 70%) with filter blur(40px), colors rgba(168,85,247,0.35) purple, rgba(56,189,248,0.32) sky blue, rgba(52,211,153,0.30) green. Animate each blob's x and y between gentle offsets (roughly -12% to 22% of the container) on infinite easeInOut loops with different durations (14s, 18s, 16s) so the light fields drift and overlap like a slow aurora. Animate only transform properties for GPU-friendly motion.
