# 网格主位放大

2×3 网格中点击某格，它弹性占据左侧主区域，其余五格退到右列小格，文字内容交叉淡入淡出。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/layout/LayoutGrid.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：click

## 原始实现提示词

Create a React component called LayoutGrid using React + Tailwind CSS + Framer Motion, recreating the Aceternity "Layout Grid". Render 6 abstract tiles (muted low-saturation gradients — mist #E4EBF2→#D8E2EA, sand #F0EAE0→#E7E0D3, sage #E8EDE3→#DDE5D8, clay #F1E6DE→#E8DAD2, ink #E4E4E7→#D4D4D8, dawn #ECECEF→#DEDEE2 — each rounded-xl with a hairline zinc-950/10 border, a mono uppercase tag like "GRID · 01" and a short title) inside a 280px-tall container (max-width 560px) split into a large main slot on the left (grid-template-columns 1.6fr 1fr, 12px gap) and a 2-column mini grid on the right holding the remaining five tiles. Track the active index in useState. Wrap everything in a Framer Motion LayoutGroup and give every tile a stable layoutId (layout-grid-{i}) plus the layout prop: when a mini tile is clicked it springs into the main slot while the previous main tile and the other minis reflow into the right column — a true grid layout tween with a spring of stiffness 210 and damping 24. Crossfade each tile's content with AnimatePresence mode="wait" keyed on its big/small state (220ms opacity): the main tile reveals its 15px semibold title plus a one-line 12px zinc-600 description, while minis show only an 11px semibold title. Tiles are buttons with cursor-pointer; transform/opacity only besides the layout animation.
