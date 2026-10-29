# 高能定格

HYPERDRIVE 字母先以 20ms 一帧高速乱序约 600ms，再从左到右逐字定格（60ms 错峰），zinc-400 乱码落定为 zinc-950，入视口自动触发。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/text/HyperTextPreview.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React component called HyperText using React + Tailwind CSS. It renders 'HYPERDRIVE' in monospace (28px, font-medium, uppercase, tracking 0.18em) as per-letter inline-block spans of fixed 1.05em width so scrambling never shifts layout. When the component enters the viewport (IntersectionObserver hook) start a 20ms setInterval: for the first ~600ms every letter is a random glyph from 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#$%&*' colored zinc-400; then letters lock left-to-right with a 60ms stagger (lock time = 600ms + index * 60ms) into the correct zinc-950 character. Write textContent and toggle classes DIRECTLY through span refs — zero React state, no re-renders per frame; clear the interval when all letters are locked and on unmount. Below the word show a status line (11px mono, uppercase, tracking 0.22em, zinc-400) that reads 'SCRAMBLING…' during the run and '— ALL SYSTEMS LOCKED' after (via a ref, not state). Replay by remounting the component. Light background, paragraph carries an aria-label of the final word.
