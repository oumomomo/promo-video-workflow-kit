# 极光流动

标题字面填充低饱和青→蓝→紫极光渐变，6 秒匀速扫过一个完整周期无缝循环；旁边一行静态灰小字作对照，更显克制高级。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/text/AuroraFlowPreview.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React component called AuroraFlowText using React + Tailwind CSS + Framer Motion. It renders a large headline ('极光流动', 44px, font-bold, tracking -0.02em) filled with a slow LOW-SATURATION aurora gradient via background-clip: text: linear-gradient(90deg, #8ED4C4 muted teal, #9DC3E6 mist blue, #BFB0E4 dusty violet, wrapping back to #8ED4C4 at 100% so the sweep loops seamlessly), backgroundSize '300% 100%', transparent text color. Animate backgroundPosition through ['0% 50%', '300% 50%'] with Framer Motion — duration 6s, ease linear, repeat Infinity — one full uniform pass per cycle with no jump (the wrapped gradient makes 300% identical to 0%). Below the headline render a plain comparison line ('同一句话，静态灰的对照', 14px, zinc-400) plus a tiny mono caption 'STATIC · ZINC-400' (11px, uppercase, tracking 0.22em, zinc-300) so the aurora reads as even quieter by contrast. Saturation must stay low — never neon; light background only, aria-label on the headline.
