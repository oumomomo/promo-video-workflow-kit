# 乱序解码

字符先显示为随机符号，再逐位“解码”成正确文字，有黑客终端的感觉。点击预览窗重播。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/text/TextScramblePreview.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：click

## 原始实现提示词

Create a React text-scramble component. When triggered, each character of
the target string cycles through random glyphs from the set "!<>-_\\/[]{}=+*^?#"
every 30ms, then locks into the correct character left-to-right, finishing
the full string in ~1.4s. Expose a trigger function and an optional
useInView auto-trigger. Monospace font, Tailwind styling.
