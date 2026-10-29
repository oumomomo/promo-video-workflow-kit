# 聚光灯显字

一句话以浅灰铺底，深色真身只在一圈 140px 的径向光斑内显形，光斑实时跟随指针——文字在你指向的地方被点亮。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/text/SpotlightTextPreview.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：move

## 原始实现提示词

Create a React component called SpotlightText using React + Tailwind CSS. It renders a paragraph-sized sentence (28px, medium, tracking -0.01em, line-height 1.65, centered, e.g. '动效是界面的呼吸，让每一次交互都拥有生命。') twice in a relative wrapper: the base copy in zinc-300, and an absolutely-positioned identical top copy in zinc-950 that is revealed only inside a radial-gradient mask — mask-image (plus -webkit-mask-image): radial-gradient(circle 140px at var(--sx) var(--sy), black 0%, black 42%, transparent 100%). On pointermove, compute the pointer position relative to the container and write it to the --sx/--sy CSS custom properties directly on the element via ref + style.setProperty (NO React state per move — zero re-renders, 60fps); on pointerleave park the vars at -9999px so the spotlight turns off. Initialize both vars to -9999px. Add a small hint label '移动鼠标阅读' (11px mono, uppercase, tracking 0.14em, zinc-400, bottom center) that fades to opacity 0 over 500ms after the first pointer move (one state flip only). cursor-crosshair over the area, select-none on the text, light background, aria-label carries the full sentence since the top copy is aria-hidden.
