# 环形文字轨

字符逐个按角度定位排成一圈（MOTION VAULT · INSPIRATION ·），整体 12 秒一圈持续旋转，中心一颗小 logo 点，悬停平滑反转方向。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/text/OrbitTextPreview.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：auto

## 原始实现提示词

Create a React component called OrbitText using React + Tailwind CSS. It typesets the phrase 'MOTION VAULT · INSPIRATION · ' around a circle WITHOUT SVG textPath: split into characters and absolutely position each at left-1/2 top-1/2 of a 216x216px relative wrapper with transform 'translate(-50%, -50%) rotate(i * (360 / len) deg) translateY(-88px)' (monospace 13px, font-medium, uppercase, zinc-950, space chars rendered as-is since the fixed angular step keeps spacing). Rotate the whole ring continuously at 360deg per 12s with a requestAnimationFrame loop (gated by IntersectionObserver, cancelAnimationFrame on cleanup) writing style.transform = rotate(angle) directly to a ref'd wrapper — no state. Track a target direction in a ref (+1 normally, -1 while hovered via onMouseEnter/onMouseLeave) and exponentially lerp the current direction each frame (factor ~dt * 4, dt clamped to 50ms) so the spin reverses like a turntable changing direction, never a hard cut. Place a small 8px rounded-full zinc-950 dot (logo mark, pointer-events-none) in the exact center. will-change-transform on the ring, cursor-pointer, light background, aria-label on the container.
