# 悬浮 Dock 栏

macOS 式 Dock：七枚锌色渐变图标排于底部，鼠标掠过时按距离放大（48 → 72px）并上浮，丝滑无 setState。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/layout/DockBar.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：move

## 原始实现提示词

Create a React component called DockBar using React + Tailwind CSS + Framer Motion + lucide-react, recreating the macOS dock magnification. Render a frosted bar (white/75, backdrop-blur, 1px zinc-200 border, rounded-2xl, soft shadow, px-4 py-3, gap-3) bottom-centered in the preview (items-end, pb-12), holding 7 icon tiles (Home, Search, Compass, Music, Camera, Mail, Settings from lucide-react, white zinc-100 strokes at 50% size) on muted zinc gradient tiles (e.g. zinc-600→zinc-800, zinc-500→zinc-600, zinc-700→zinc-900 variants, rounded-xl, soft inner shadow). Keep a single mouseX useMotionValue on the bar: set it to e.clientX on pointermove and to Infinity on pointerleave — never useState in the pointer path. Each icon is a memoizable child holding a ref to its div: derive distance = useTransform(mouseX, x => x − rect.x − rect.width/2) measured live from getBoundingClientRect, then size = useSpring(useTransform(distance, [−110, 0, 110], [48, 72, 48]), { mass: 0.1, stiffness: 170, damping: 13 }), bound to width/height via style. Because the bar uses items-end alignment, magnified icons grow upward and lift off the baseline automatically — smooth 60fps magnification that ripples to neighbors by distance.
