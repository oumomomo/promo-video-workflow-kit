# 昼夜流转

16 秒一轮的天光：晨曦、正午、暮色、星夜依次流转，日月交替掠过天际。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/background/DayNight.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React component called DayNight using React + Tailwind CSS with scoped CSS keyframes (inline <style> tag, 16s linear infinite cycle). Stack four absolutely positioned sky layers and crossfade them with opacity keyframes: dawn (soft peach linear-gradient #FCE9D8 → #F5AE8B, visible 0-25%), noon (pale sky #D9ECF9 → #F1F8FD, 25-50%), dusk (warm violet #B99BD6 → #F0A184, 50-75%), night (deep zinc-950 #09090B → #17171B, 75-100%) with ~8% crossfade overlaps so colors interpolate smoothly. Add a stars layer (tiny 1-1.5px white radial-gradient dots scattered over the upper half) that fades in only during night. A small sun disc (24px, radial #FDE9C8 → #F9B45C with a warm box-shadow glow) sits at the top of a full-size arm whose transform-origin is 50% 150% — rotating the arm from -78deg to 78deg sweeps the sun across the sky in an arc, fading in/out near the horizons during the dawn→dusk half; a smaller moon (20px, #FAFAFA → #D4D4D8) does the same during the night quarter. Transform-only animation. Place mock content (small heading + outline button) on top with mix-blend-difference and white text so the foreground automatically reads dark on light skies and light on the night sky.
