# 滚动堆叠卡

向下滚动时卡片一张张堆叠压上，前一张微微缩小压暗——经典的滚动叙事。

来源：https://github.com/xiyu519/MotionVault/blob/0a201da92e4b4fa7436b1c79c7f249bc66329644/src/components/effects/card/StackingCards.tsx

版本：0a201da92e4b4fa7436b1c79c7f249bc66329644

许可：MIT（保留上游 LICENSE）

触发：scroll

## 原始实现提示词

Create a React stacking-cards effect inside a scrollable container (320px,
overflow-y scroll). Four cards are position sticky at top 16px; as scroll
progress pushes a new card up, the covered card scales to 0.94 and dims to
brightness 0.96. Drive progress with GSAP ScrollTrigger using the container
as scroller (or a scroll handler + math). Each card: white, 1px border,
rounded-12, numbered 01-04.
