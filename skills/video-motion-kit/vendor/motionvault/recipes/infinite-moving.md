# 无限横滚卡带

六张卡片带以 30 秒一圈无缝横滚（双拷贝位移折返），悬停减速至 0.2 倍，两端渐隐遮罩。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/layout/InfiniteMoving.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React component called InfiniteMoving using React + Tailwind CSS + Framer Motion, recreating the Aceternity "Infinite Moving Cards". Render 6 abstract cards (200×130px, rounded-xl, hairline zinc-950/10 border, soft shadow, muted low-saturation gradients — mist/sand/sage/clay/ink/dawn variants — each with a mono uppercase tag like "TAPE · 01", a 13px semibold title and one skeleton bar) on a horizontal flex track with 16px gaps, duplicated once so two identical copies sit back to back (one copy = 6 × 216px = 1296px wide). Drive the loop with Framer Motion's useAnimationFrame on an x MotionValue: advance x leftward at 1296px per 30s (≈43.2px/s... i.e. COPY_W / 30000 px per ms × delta), and when x passes -COPY_W add COPY_W back so the tape wraps seamlessly — never use setState in the frame loop. Keep a speed factor in a ref that eases (lerp 0.06 per frame) toward 0.2 while the wrapper is hovered and back to 1 on leave, multiplying the per-frame delta so the tape smoothly decelerates to a crawl instead of snapping. Gate the frame loop with an IntersectionObserver in-view flag. Overlay both ends with pointer-events-none gradient masks (64px wide, from the preview background #FAFAFA to transparent) so cards fade in and out at the edges. Isolate the perpetual animation in a React.memo'd micro-component so parent re-renders never reset it.
