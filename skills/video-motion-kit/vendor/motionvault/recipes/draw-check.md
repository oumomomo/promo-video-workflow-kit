# 描绘打勾

圆圈先描出轮廓，对勾随即一气呵成，结尾带一点回弹缩放的“咔哒”感与一抹极淡的绿色。点击图标即可重播。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/svg/DrawCheckPreview.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：click

## 原始实现提示词

Create a React component called DrawCheck using React + Tailwind CSS + Framer Motion. It renders a 64x64 SVG (viewBox 64) inside a rounded-full button. Sequence on mount: 1) a circle outline (radius 27, 2.5px zinc-950 stroke, round cap, rotated -90deg) draws itself via pathLength 0 to 1 over 0.6s ease-in-out; 2) a check mark path 'M 21 33 L 28.5 40.5 L 44 24' (3px zinc-950, round caps/joins) draws via pathLength 0 to 1 over 0.35s at 0.6s delay; 3) at ~0.95s the wrapping motion.g pops with a slight overshoot — scale keyframes [1, 1.12, 1] over 0.35s, transform origin 50% 50% — while a same-radius circle filled #16A34A fades to opacity 0.08 as a subtle success tint. Clicking the button increments a runId in state and keys the svg on it so the whole sequence replays. Light background, animate pathLength/opacity/transform only.
