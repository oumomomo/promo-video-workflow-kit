# 遮罩揭示

浅灰描边的 HIDDEN 铺底，实心黑字只在一枚跟随指针的径向渐变光斑内显形——聚光灯下现出真身。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/svg/MaskRevealPreview.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：move

## 原始实现提示词

Create a React component called MaskReveal using React + Tailwind CSS + SVG. It renders a 320x160 viewBox SVG with the word 'HIDDEN' (56px, bold, letter-spacing 0.14em, centered via textAnchor middle + dominantBaseline central) stacked in two layers: a base layer drawn as a pale outline (fill none, 1px stroke #D4D4D8 zinc-300) and an identical top layer filled solid #09090B (zinc-950). The top layer carries mask='url(#spot-mask)' where the mask is a single circle (r 58 in viewBox units) filled with a radialGradient (white opacity 1 at 0% and 55%, fading to opacity 0 at 100%) — so the solid glyph only materializes inside a soft spotlight. On pointermove over the wrapper, convert the pointer to viewBox coordinates ((clientX - rect.left) / rect.width * 320, same for y) and write them to the mask circle's cx/cy via ref + setAttribute (NO React state per move, zero re-renders); on pointerleave park the circle at -9999 so the spotlight turns off. Initialize cx/cy at -9999. Use component-unique ids for the gradient and mask to avoid collisions. cursor-crosshair, select-none, light background, role=img with an aria-label since the masked copy is decorative.
