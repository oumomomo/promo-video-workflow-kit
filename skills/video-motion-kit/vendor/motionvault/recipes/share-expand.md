# 分享展开按钮

点击后按钮弹性展开为一排分享图标，逐个弹出；再点即可收回。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/button/ShareExpand.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：click

## 原始实现提示词

Create a React component called ShareExpand using React + Tailwind CSS + Framer Motion + lucide-react. A single spring (type spring, stiffness 500, damping 25) drives everything. Collapsed: a dark zinc-950 pill (h-11, rounded-full) with a Share2 icon and the label '分享'. On click the wrapper (motion.div with layout, overflow-hidden, h-11 rounded-full) morphs elastically into an open tray — bg-zinc-100 with a 1px zinc-200 border and p-1 — containing four channel icon buttons (Link2, Send, MessageCircle, Mail; h-9 w-9 rounded-full, zinc-600 icons, hover bg-white) that pop in with scale 0→1 + opacity on a 60ms stagger, followed by a trailing X close button at 4×60ms. Swap the two states with AnimatePresence mode popLayout; clicking any icon or the X springs the pill back closed. Keep the whole interaction keyboard-focusable with aria-labels on icon buttons.
