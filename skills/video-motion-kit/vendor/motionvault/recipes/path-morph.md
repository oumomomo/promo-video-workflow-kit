# 路径变形

一个有机的 Blob 与一颗四角星共用同一套路径命令，d 属性在两者之间平滑插值，每 3 秒循环一次。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/svg/PathMorphPreview.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React component called PathMorph using React + Tailwind CSS + Framer Motion. It renders a 200x200 SVG with a single filled motion.path (fill #09090B at 90% opacity). Craft TWO compatible 'd' strings with the exact same command structure — 8 anchors every 45deg around center (100,100) connected by 8 cubic C segments, closed with Z: a blob (radii alternating 68/58/48/58 with generous tangential control points ~0.42*r) and a 4-point star (radii alternating 70/38 with short control points ~0.16*r producing curved points). Because the structures match, Framer Motion can tween the 'd' attribute directly: toggle a boolean in state every 1.5s (1.2s morph + 0.3s hold, full loop 3s) via setInterval and animate d to the current shape's string with duration 1.2s, ease-in-out; clean up the interval on unmount. Below the shape show a tiny mono uppercase label (text-xs zinc-400) that crossfades between 'BLOB' and 'STAR' with AnimatePresence mode='wait' (y 4px drift, 200ms) so the label always names the current shape. Light background.
