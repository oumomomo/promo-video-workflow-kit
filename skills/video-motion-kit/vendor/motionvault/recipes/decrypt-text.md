# 解密文字

悬停时字符以 30ms 一帧高速随机置换，再从左到右逐位“解密”定格成原文——加密情报既视感，解完后保持。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/text/DecryptTextPreview.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：hover

## 原始实现提示词

Create a React component called DecryptText using React + Tailwind CSS. It renders a monospace uppercase sentence (e.g. 'MOTION IS THE MESSAGE', 18-24px, font-medium, tracking 0.14em, zinc-950, centered) that starts fully readable. On mouse enter, a 30ms setInterval starts a decode run: each frame every non-space character is replaced by a random glyph from '!<>-_\\/[]{}=+*^?#@$%&' until it locks — characters lock left-to-right, each scrambling for ~8 frames with a 2-frame offset per position (lock frame = 8 + index * 2), so the plaintext crystallizes progressively like intercepted intel being decrypted. When the last character locks, clear the interval, restore the exact target string and keep it (leaving and re-entering replays the run; a run already in progress is not restarted). Guard the interval with a ref, clean it up on unmount. Under the sentence show a small status line (11px mono, uppercase, tracking 0.22em, zinc-400) reading 'HOVER TO DECRYPT' that switches to '— DECODED' once a run completes (single state flip). cursor-pointer, select-none, light background, role=button with an aria-label.
