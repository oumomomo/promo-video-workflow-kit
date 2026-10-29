# 极光渐变文字

低饱和极光色渐变在字面缓缓流动，8 秒一循环，身后叠一层 20% 透明度的模糊辉光，梦幻而不刺眼。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/text/AuroraTextPreview.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React component called AuroraText using React + Tailwind CSS + Framer Motion. It renders large text (40px, font-semibold, tracking -0.02em) filled with a flowing low-saturation aurora gradient via background-clip: text: linear-gradient(90deg, #7DD3C0 soft teal, #93C5E8 sky, #C4B5E8 lilac, #E8B4C8 rose, wrapping back to #7DD3C0 at 100% for a seamless loop), with backgroundSize '300% 300%' and transparent text color. Animate backgroundPosition through ['0% 50%', '100% 50%', '0% 50%'] with Framer Motion — duration 8s, easeInOut, repeat Infinity — so the wash drifts slowly back and forth with no visible jump. Behind the text, render a duplicate absolutely-positioned aria-hidden copy with the same gradient and animation, at opacity 0.2 with a blur-md filter, as a barely-visible glow. Both copies live in a relative inline-block wrapper with an aria-label for accessibility. Smooth, dreamy, never garish; light background only.
