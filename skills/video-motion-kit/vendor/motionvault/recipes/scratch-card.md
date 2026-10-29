# 刮刮卡

一张盖着银灰刮刮层的奖品卡：按住拖动刮开金属涂层，露出底下的「再来一瓶」；刮开超过 45% 后剩余涂层自动淡出，可一键重来。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/card/ScratchCard.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：move

## 原始实现提示词

Create a React component called ScratchCard using React + Tailwind CSS + Canvas 2D. Render a prize card (320×200px, rounded-xl, 1px zinc-200 border) whose prize layer (warm amber-to-rose gradient, small mono uppercase 'YOU WIN' label, big bold '再来一瓶 🎉', and a mono serial line) sits under a scratch-off foil. Implement the foil as an absolutely positioned canvas (dimensions set via inline style, DPR-aware): paint a zinc metallic linear-gradient (#d4d4d8 → #e4e4e7 → #f4f4f5 → #d4d4d8 → #a1a1aa), sprinkle ~1400 1px noise specks, and draw a centered '刮 开 惊 喜' hint plus 'SCRATCH HERE' in mono. On pointerdown capture the pointer and start erasing: set globalCompositeOperation to 'destination-out' and fill 28px-radius circles at the pointer; on pointermove interpolate circles along the drag segment (step = radius/2) so fast strokes erase continuously. Track progress with a coarse 24×15 boolean grid whose cells within the erase circle get marked; when over 45% of cells are scratched, set state once to fade the whole canvas to opacity 0 (700ms CSS transition) and disable pointer events. Show a small '再来一次' reset button (RotateCcw icon, mono uppercase, frosted white) once finished, which repaints the foil and re-arms scratching. No setState in the pointermove path besides the one-time completion flag.
