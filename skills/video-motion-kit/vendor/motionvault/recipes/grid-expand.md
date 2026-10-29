# 点击展开画廊

2×2 的渐变小卡，点击任意一张便以共享布局动画放大铺满预览窗，其余退成 30%。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/layout/GridExpand.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：click

## 原始实现提示词

Create a React component called GridExpand using React + Tailwind CSS + Framer Motion. Render a 2×2 CSS grid (height 240px, max-width 520px, gap 12px) of cards, each a soft low-saturation gradient (sand #F0EAE0→#E7E0D3, sage #E8EDE3→#DDE5D8, sky #E4EBF2→#D8E2EA, clay #F1E6DE→#E8DAD2, all 135deg) with rounded-xl corners, a hairline border (black 5%) and a small mono label like "A · 01" (11px, zinc-500) anchored bottom-left. Wrap everything in a Framer Motion LayoutGroup and give each grid card a layoutId like grid-expand-{i}. When a card is clicked (index in useState), swap its grid cell for an empty placeholder div and mount an absolutely positioned overlay (inset 16px, z-10) with the SAME layoutId so it FLIP-morphs from the grid cell to fill the preview area over 500ms with ease-in-out cubic-bezier(0.42, 0, 0.58, 1); the unopened grid cards fade to 30% opacity. The expanded overlay reveals, with a 200ms delayed fade + 10px rise, the mono label, an 18px semibold title (zinc-800) and a 13px two-sentence description (zinc-600, line-height 1.7), plus a circular close button (28px, white/70 with backdrop-blur, hairline border, an X icon from lucide-react) at the top-right. Clicking the X — or anywhere on the expanded card — unmounts the overlay inside AnimatePresence so it morphs back into its grid cell.
