# 点赞爆裂

推特式点赞——爱心弹性填充、光环向外扩散、7 颗粒子四溅，旁边的计数器随数字上下滑动切换；再点一次则平静收回。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/button/LikeButton.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：click

## 原始实现提示词

Create a React LikeButton component (Twitter-style) using React + Tailwind CSS + Framer Motion + the Heart icon from lucide-react. A ghost circular button (h-12 w-12, rounded-full, hover bg-rose-50) with a heart icon and a like count sitting next to it. On like: the heart fills rose #F43F5E and pops in with an elastic spring (remount with scale 0, spring stiffness ~420 / damping ~11 so it overshoots to ~1.3 before settling), a 2px rose ring expands outward from the button's edge (scale 1 → 1.9 while fading, 550ms ease-out), and 7 tiny particles — a mix of 4px dots and mini filled hearts in rose shades (#F43F5E, #FB7185, #FDA4AF) — spew radially (even 360°/7 spread with slight angle jitter, 26–44px travel, shrinking and fading over 650ms ease-out). On unlike: the heart unfills with a calm 150ms shrink, no ring or particles. The count increments/decrements with a tiny y-slide: wrap it in AnimatePresence (popLayout) so the new number slides in from below on +1 and from above on -1 (180ms). Center on a light preview.
