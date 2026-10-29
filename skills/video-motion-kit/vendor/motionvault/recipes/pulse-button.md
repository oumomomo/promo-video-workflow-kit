# 脉冲按钮

按钮外圈两环脉冲波周期扩散，按钮本体纹丝不动——动静反差即是强调。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/button/PulseButton.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React component called PulseButton using React + Tailwind CSS with scoped CSS keyframes (inline <style> tag — Magic UI Pulsating Button, inverted: the button stays still). Wrap a dark zinc-950 button (h-11, rounded-lg, px-8, white text) in a relative div. Add two absolutely positioned ring spans matching the button shape (inset-0, rounded-lg, 1.5px border rgba(113,113,122,0.55), pointer-events-none). Each ring runs a 2s cubic-bezier(0.16,1,0.3,1) infinite pulse keyframe — scale 1 → 1.8 with opacity 0.5 → 0 — the second ring delayed 1s so the sonar waves never overlap in phase. The button itself is motionless except a hover bg shift (zinc-800) and active:scale-[0.97]; the stillness against the pulsing rings is the effect. Transform + opacity only, will-change set, honor prefers-reduced-motion.
