# 翻牌显示

机场翻牌钟：深色小牌上的字母绕中间铰链向下翻转入场，列间 80ms 涟漪错峰，每词停留 2 秒后翻到下一个词。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/text/SplitFlapPreview.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React component called SplitFlap using React + Tailwind CSS + Framer Motion. It mimics an airport split-flap departure board cycling through three words ('DESIGN' → 'MOTION' → 'CRAFT', padded to 6 columns with spaces). Each letter lives in a dark tile (40x56px, bg zinc-900, rounded-md, subtle inset top highlight + soft drop shadow) containing a white monospace 24px letter. On every word change each tile's letter is remounted (key includes word index + column) and animates with Framer Motion from rotateX -90deg + opacity 0.35 to rotateX 0 + opacity 1 — duration 450ms, ease [0.2, 0.7, 0.3, 1], transformOrigin center, backfaceVisibility hidden, parent tile gets perspective 400 — so the letter folds down around the board's middle like a physical flap. Add an 80ms delay per column for a left-to-right ripple, a 1px black/60 horizontal hinge line across the tile's vertical center, and a faint white gradient shading on the upper half. A setInterval cycles the word every ~3s (2s hold + flip time) with cleanup on unmount. Animate transform/opacity only, light page background, aria-label announces the current word.
