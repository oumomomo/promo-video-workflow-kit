# 像素消散卡

卡片内容被预渲染成一块画布：悬停时鼠标附近的 10px 碎块随机飞散淡出，松手后弹性归位、重组复原。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/card/DecayCard.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：hover

## 原始实现提示词

Create a React component called DecayCard using React + Tailwind CSS + Canvas 2D. Render a card (320×200px, rounded-xl, 1px zinc-200 border, white bg) whose entire content is a single canvas (inline-style dimensions, DPR-aware). Pre-render the content into an offscreen canvas: dark zinc-900 face, a soft radial gradient orb with a 1px white/20 ring, a mono uppercase label, a semibold title and two skeleton bars. Slice the offscreen into 10px chunks (~32×20) tracked in Float32Arrays: offset x/y, velocity x/y, alpha and alpha-velocity. On pointermove, chunks within 64px of the cursor get kicked: a radial push (falloff 1 − d/64, magnitude 6–16px plus random jitter) and an alpha impulse (−0.25 to −0.7), so nearby pixels scatter and fade. Each frame integrate a spring back to origin (v += −offset×0.055, v ×= 0.88) and to full opacity (va += (1−a)×0.07, va ×= 0.82), drawing each chunk with drawImage at its displaced position and globalAlpha. When every chunk has settled (|offset| < 0.2, alpha > 0.995) stop the rAF loop and draw the pristine image — the card disintegrates under the cursor and elastically reassembles on release. No React state in the pointer path.
