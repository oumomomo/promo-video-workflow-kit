# 钱包抽卡

三张银行卡插在钱包夹层里，各露出 28px 卡边；点击露出的卡边，那张卡向上抽出并完整呈现卡面细节，再点一次或点其他卡便归位。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/card/WalletPull.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：click

## 原始实现提示词

Create a React component called WalletPull using React + Tailwind CSS + Framer Motion. Render three bank cards (300×176px, rounded-xl, muted gradients — charcoal zinc-700→zinc-900, slate-400→slate-600, sand #CDBD9E→#A89472 — each with a tiny gradient chip graphic, mono card number, holder name, expiry and balance) stacked inside a wallet pocket (a wider rounded-2xl zinc-100 panel behind the bottom of the stack). Each card peeks 28px above the one in front of it: card i sits at y = 36 + (2 - i) * 28 with zIndex 10/20/30 so all three tops are visible and clickable. Track which card is out with a single useState (number | null) — only one card out at a time. Every card is a motion.div with initial={false} and a spring transition (stiffness 320, damping 26): clicking a peeking edge springs that card up to y 0 with scale 1.03 and zIndex 40, fully revealed, while the other cards sink 10px, scale to 0.97 and dim to 0.55 opacity; clicking the out card again (or another card) slots it back. The card's detail row (holder / expiry / balance) fades from 0.35 to full opacity only while the card is out.
