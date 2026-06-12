# 反套路实现规约（Anti-Slop Craft Layer）

ui-worker 出原型代码时的"craft 强制层"。目标：纠正 LLM 写前端时的统计偏好，产出不像 AI 套模板、对标 dribbble 头部的界面。

> 来源与归属：本模块的规则体系改编自开源项目 **taste-skill**（github.com/Leonxlnx/taste-skill，MIT License, © 2026 Leonxlnx），按本仓库的中文、跨栈与品牌需求重写并扩展。

## 适用边界（先读这条）

1. **品牌优先于本规约**：当任务有明确品牌系统时（如示例品牌（ExampleBrand）的深色科技风格、`video_design_system.md`），品牌规范覆盖本模块里与之冲突的禁令（尤其"禁 AI 紫蓝/禁霓虹发光"）。本模块是**默认 web/产品 UI**的 craft 基线，不是品牌的上位法。
2. **意图可迁移、写法按栈适配**：下文示例多用 React/Tailwind/Framer Motion 表达，但规则约束的是**设计意图**。落到 Vue / Svelte / 纯 HTML / Remotion 时，迁移意图、按目标栈改写具体类名与 API，不要硬抄 className。
3. **不确定的视觉方向问一句再动手**，确定后严格执行，不在生成中途反复横跳风格。

## 拨盘（三个全局变量，驱动下面所有规则）

每次生成前先定档，没特别要求时用默认值；用户在对话里明确要求则动态覆盖。

- **DESIGN_VARIANCE 布局变化度**：默认 7（1=完美对称，10=艺术化失衡）
- **MOTION_INTENSITY 动效强度**：默认 5（1=静态仅 hover，10=电影级滚动编排）
- **VISUAL_DENSITY 信息密度**：默认 4（1=画廊留白，10=驾驶舱密排）

## 1. 配色校准

- **最多 1 个强调色**，饱和度 < 80%；中性基底用 Zinc/Slate 一套灰阶，禁止同一项目里冷暖灰乱跳。
- **禁 "AI 紫蓝"**：默认不要紫色按钮辉光、霓虹渐变。强调色用克制的高对比单色（祖母绿 / 电光蓝 / 深玫瑰等）。**（品牌例外见适用边界）**
- **禁纯黑 `#000000`**：用 Zinc-950 / 炭黑 / 近黑。
- **阴影染色**：用阴影时把色相往背景色调，不要纯黑投影、不要外发光辉光。
- 60/30/10 面积法则：基底 60、辅助 30、强调 10；强调色只落在 CTA 和关键焦点。

## 2. 排版

- **字体**："Premium/Creative"语境别默认 Inter；用 Geist / Outfit / Cabinet Grotesk / Satoshi 等更有性格的字。仪表盘/软件 UI **禁衬线**，用高端无衬线配对（Geist + Geist Mono、Satoshi + JetBrains Mono）。衬线只给编辑/创意类。
- **标题**：靠字重和对比建立层次，别一味堆超大字号；H1 不该"尖叫"。展示标题默认 `text-4xl md:text-6xl tracking-tighter leading-none` 之类的紧排。
- **正文**：行宽限制 `max-w-[65ch]`，行高 `leading-relaxed`，正文色用中灰而非纯黑。
- **数字**：高密度场景（VISUAL_DENSITY > 7）所有数字用等宽 `font-mono`。

## 3. 布局

- **去中心化**：DESIGN_VARIANCE > 4 时禁止居中 Hero/H1，改用分屏 50/50、左文右图、非对称留白。
- **栅格优于 flex 数学**：结构用 CSS Grid（`grid grid-cols-1 md:grid-cols-3 gap-6`），不要 `w-[calc(33%-1rem)]` 这种百分比硬算。
- **禁通用三栏卡片**：经典"横排三张等宽卡"功能区禁用，改 2 栏 Zig-Zag、非对称网格或横向滚动。
- **容器收口**：页面用 `max-w-[1400px] mx-auto` 或 `max-w-7xl` 居中约束。
- **视口稳定**：满高区段用 `min-h-[100dvh]`，**绝不用 `h-screen`**（iOS Safari 会跳版）。
- **移动端兜底**：高变化度布局在 `< 768px` 必须塌成单列（`w-full px-4 py-8`），杜绝横向滚动。

## 4. 材质与卡片（反"卡片滥用"）

- 卡片**只在用层级/抬升表达信息时才用**；能用留白、`border-t`、`divide-y` 分组就别套盒子。高密度（>7）禁通用卡片容器。
- 玻璃拟态要"真"：除了 `backdrop-blur`，加 1px 内边框（`border-white/10`）和内阴影（`shadow-[inset_0_1px_0_rgba(255,255,255,0.1)]`）模拟边缘折射。
- 圆角统一成标度；用阴影时宽而淡、向背景色染色（如 `shadow-[0_20px_40px_-15px_rgba(0,0,0,0.05)]`）。

## 5. 交互状态（必须全覆盖）

LLM 天然只生成"成功静态态"，必须补全：

- **加载**：用骨架屏匹配真实布局尺寸，别用通用转圈。
- **空状态**：精心构图，并指引如何填充数据。
- **错误**：行内清晰报错（如表单输入框下方）。
- **触觉反馈**：`:active` 用 `-translate-y-[1px]` 或 `scale-[0.98]` 模拟物理按下。
- **表单**：label 在 input 上方、错误文案在下方、输入块 `gap-2`。

## 6. 动效

- **缓动**：禁线性。CSS 用 `cubic-bezier(0.16, 1, 0.3, 1)`；JS 动效用 spring（`stiffness:100, damping:20`）。入场 ease-out、出场 ease-in，时长 150–300ms。
- **磁吸/连续动效**（MOTION_INTENSITY > 5）：绝不用 React `useState` 驱动连续动画，用 Framer `useMotionValue`/`useTransform` 跳出渲染循环。
- **错落入场**：列表/网格用 `staggerChildren` 或 `animation-delay: calc(var(--index)*100ms)` 瀑布式揭示，别瞬间全挂载。
- **滚动**：复杂滚动编排用 Framer/GSAP，**禁 `window.addEventListener('scroll')`**。GSAP/ThreeJS 与 Framer 不在同一组件树混用。

## 7. 性能护栏

- **只动 `transform` 和 `opacity`**，绝不动画 `top/left/width/height`。
- 颗粒/噪点滤镜只挂在 `fixed inset-0 pointer-events-none` 的固定层，绝不放进滚动容器。
- `z-index` 克制，只给系统层级（吸顶导航、Modal、Overlay）用，别乱撒 `z-50`。
- 连续/无限动效必须 `React.memo` 并隔离进自己的微型 Client Component，绝不触发父层重渲染。

## 8. AI tells 禁用清单（一眼看穿是 AI 的痕迹）

**视觉**：禁外发光辉光、禁纯黑、禁过饱和强调色、禁大标题渐变填充文字、禁自定义鼠标光标。
**排版**：禁 Inter（替换见上）、禁无意义超大 H1、仪表盘禁衬线。
**内容数据（"Jane Doe 效应"）**：
- 禁通用人名（John Doe / Sarah Chan）→ 用真实可信的创意名。
- 禁通用头像（egg/Lucide user 图标）→ 用可信照片占位或特定风格。
- 禁假数据（99.99% / 50% / 1234567）→ 用有机的"脏"数据（47.2% / +1 (312) 847-1928）。
- 禁创业套话名（Acme / Nexus / SmartFlow）→ 造有语境的高级品牌名。
- 禁文案陈词（Elevate / Seamless / Unleash / Next-Gen）→ 用具体动词。
**外部资源**：禁 Unsplash（易失效）→ 用 `https://picsum.photos/seed/{随机串}/800/600` 或 SVG 头像。shadcn/ui 可用但禁默认态，必须改圆角/配色/阴影适配项目调性。
**图标/emoji**：代码、文案、alt 文本里**禁 emoji**，统一用图标库（Radix / Phosphor）或干净 SVG，全局统一 `strokeWidth`（如统一 1.5 或 2.0）。

## 9. 高端范式库（需要"出彩"时取用，别默认通用 UI）

- **Bento 2.0**：非对称瓦片分组（如 Apple 控制中心），标题描述放卡片外下方，大留白，卡片内 `p-8`+宽淡扩散阴影；每张卡含一个无限循环的"活"态（脉冲/打字机/浮动/轮播）。
- **导航**：Mac Dock 放大、磁吸按钮、Dynamic Island 形变、径向菜单、Mega Menu 错落展开。
- **布局**：Bento / Masonry / 分屏对向滚动 / 幕布揭示。
- **卡片**：3D 倾斜跟随鼠标、聚光边框、真玻璃折射、全息箔片、形变 Modal。
- **滚动**：吸顶堆叠、横向滚动劫持、Zoom 视差、SVG 路径自绘、液态转场。
- **文字**：动态跑马灯、文字蒙版露出视频、字符乱码解码、环形路径、渐变描边动画。
- **微交互**：粒子爆破按钮、骨架微光、方向感知 hover 填充、点击涟漪、网格 mesh 渐变背景。

> 取用原则：服务于信息层次和品牌调性，不为炫技堆砌；一屏一个视觉重心。

## 10. 出码前预检表（最后一道闸）

- [ ] 拨盘三档是否已定，且代码与档位一致？
- [ ] 配色：是否 ≤1 强调色、无 AI 紫蓝/霓虹（或品牌例外已确认）、无纯黑、阴影染色？
- [ ] 排版：是否避开 Inter/仪表盘衬线、靠字重而非纯字号建层次？
- [ ] 布局：高变化度是否去中心化、Grid 而非 flex 硬算、移动端塌单列、`min-h-[100dvh]` 而非 `h-screen`？
- [ ] 卡片是否克制（能留白/分隔线就不套盒子）？
- [ ] 空/加载/错误/active 全状态是否齐？
- [ ] 动效是否只动 transform/opacity、spring 非线性、连续动效已隔离 memo？
- [ ] 内容是否无假名/假数据/Unsplash/emoji/套话？
- [ ] 第三方库是否核对过 package.json，缺失给了安装命令？
- [ ] 对比度过 WCAG AA、焦点态可见？
