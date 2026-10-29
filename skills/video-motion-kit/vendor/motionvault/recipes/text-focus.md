# 滚动聚焦文字

长段落随滚动逐字点亮：文字从 15% 的浅灰依次沉入墨色，滚到哪里读到哪里。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/scroll/TextFocus.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：scroll

## 原始实现提示词

Create a React component called TextFocus using React + Tailwind CSS + Framer Motion. Render an internal scroll container (320px tall, overflow-y auto, overscroll-contain, thin custom scrollbar — never the page) holding a ~2.5×-tall padded column: a mono uppercase caption, then a paragraph of ~90 Chinese characters at 18px, font-medium, line-height 2. Split the text into per-character spans (a Char micro-component). Each Char calls useTransform on the shared useScroll({ container }) scrollYProgress, mapping its own slice [i/total, i/total + 1.5/total] to opacity [0.15, 1], so characters light up sequentially from faint grey to full zinc-950 ink as you scroll — the premium "read as you scroll" effect. Pure MotionValue bindings, zero re-renders. Include the sticky top progress hairline and the fading "向下滚动" hint pill.
