# ui-worker

视觉 / UI / UX 设计中枢。负责一切视觉与设计工作——UI 概念与布局、UX 流程、信息架构、视觉风格方向、设计系统/design tokens、组件规范、文案/microcopy、无障碍，以及直接产出/评审/打磨前端原型（HTML/CSS/JS、React、Next、Vue、Svelte、Tailwind）和 Remotion 视频视觉。

触发词：UI、界面、交互、原型、页面设计、前端设计、视觉、设计系统、配色、排版、design tokens、Figma、落地页、组件库、视频视觉。

## 安装与使用

将本目录复制到你的 Hermes Agent skills 目录下（通常为 `~/.hermes/skills/devops/ui-worker` 或对应分类）。

加载后即可在对话中触发使用。

## 目录结构

```
ui-worker/
├── SKILL.md                 # 主规则文件
├── reference/
│   ├── anti-slop-craft.md   # 反套路实现规约
│   ├── brand-memory/        # 品牌记忆示例（含 _TEMPLATE.md）
│   ├── design-intelligence/ # 配色、排版、风格等结构化数据（CSV）
│   ├── diagrams.md          # 流程图/示意图指南
│   ├── inspiration/         # 灵感库 + 拆解案例
│   ├── review-rubric.md     # 设计评审打分表
│   ├── scripts/             # Design Tokens 生成器等脚本
│   └── upstream-skill-content.md
└── .gitignore
```

## 设计哲学

- 对标 dribbble 头部作品的视觉质量
- 克制配色 + 慷慨留白 + 清晰层次 + 真实深度
- 品牌优先：有品牌系统时优先遵循品牌规范
- 反 AI 生成感：禁用常见套路，强调 craft 与细节

## 上游内容

- `design-intelligence/` 中的部分模式参考了公开设计系统与最佳实践
- 灵感案例仅作手法学习，不包含受版权保护的具体作品

## License

MIT License

Copyright (c) 2026 Hermes Agent Community

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
