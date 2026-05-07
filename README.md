# 🛠️ Hermes Agent 自定义 Skills

个人的 Hermes Agent 技能集合。

## Skills 列表

| Skill | 说明 | 用法 |
|-------|------|------|
| [requirement-analyst](productivity/requirement-analyst/) | 需求分析专家 — 输入想法，输出需求文档 + Excel | "我想做一个XXX，帮我出需求文档" |

## 安装

```bash
# 克隆到 skills 目录
git clone https://github.com/gatinul16-xy/hermes-skills.git ~/.hermes/profiles/alpha/skills/custom
```

或者单独安装某个 skill：

```bash
# 下载单个 skill
mkdir -p ~/.hermes/profiles/alpha/skills/productivity/requirement-analyst
curl -o ~/.hermes/profiles/alpha/skills/productivity/requirement-analyst/SKILL.md \
  https://raw.githubusercontent.com/gatinul16-xy/hermes-skills/main/productivity/requirement-analyst/SKILL.md
```
