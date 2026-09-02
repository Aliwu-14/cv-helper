# cv-helper

> 多轮引导式中文简历定制助手。可安装到 Claude Code / Codex / Cursor / OpenClaw / Harness 等具备 Skill 机制的 Agent 客户端。

## 工作方式

`cv-helper` 不是"贴一份简历 → 生成"的单次工具，而是**对话式引导协议**。加载 Skill 后，Agent 会先输出一段开场白告知用户流程，再按 6 个阶段逐项向用户提问：

1. **基本信息**（姓名 / 电话 / 邮箱 / 城市 / 学历 / 工作年限）
2. **求职方向**（行业 / 职能 / 期望城市 / 工作形式）
3. **目标公司与岗位**（公司名 / 岗位 / JD / 投递状态）
4. **希望突出的亮点**（3–5 项）
5. **履历内容**（教育 / 经历 / 技能 / 奖项）
6. **生成与 ATS 校验**

全部收集完成后，Agent 会研究公司 + 生成六段模块简历（个人总结 / 基本信息 / 教育 / 经历 / 技能 / 奖项） + 跑 ATS 校验 + 让用户迭代。

## 功能概览

| 文件 | 说明 |
|------|------|
| `SKILL.md` | Skill 入口文件，定义触发条件、开场白、6 阶段流程、输出契约 |
| `references/intake_flow.md` | 6 阶段状态机与提问脚本蓝本 |
| `references/install.md` | Claude / Codex / Cursor / OpenClaw / Harness 五处安装指南 |
| `references/methodology.md` | 方法论与写法的总论 |
| `references/patterns.md` | 模块结构、bullet 模式与示例模板 |
| `references/lexicon.md` | 行业缩写与术语 |
| `references/ats_layout.md` | ATS 格式与排版硬约束 |
| `references/recruiter_habits.md` | HR 阅读模型与秒级扫读偏好 |
| `references/interview_prep.md` | 简历 → 面试预测问题库 |
| `references/templates.md` | LaTeX / Marp / HTML 三套简历导出模板 |
| `references/examples.md` | 输出示例 |
| `scripts/validate_output.py` | 中文四行总结校验器 |
| `scripts/validate_section.py` | 中文非总结模块校验器 |
| `scripts/validate_output_en.py` | 英文四行总结校验器 |
| `scripts/validate_section_en.py` | 英文非总结模块校验器 |
| `scripts/test_*.py` | 校验器回归测试套件（88 个测试） |

## 快速开始

### 用户端

把你的 Agent 客户端打开，对话中输入：

> 帮我用 cv-helper 生成一份简历

或更具体：

> 我想投字节跳动的产品经理岗位，帮我用 cv-helper 生成一份简历。

Agent 会回复开场白并开始按 6 阶段逐项提问。

### 安装

详见 [references/install.md](references/install.md)。一行克隆：

```bash
# Claude Code
git clone https://github.com/Aliwu-14/cv-helper.git ~/.claude/skills/cv-helper
# Cursor
git clone https://github.com/Aliwu-14/cv-helper.git ~/.cursor/skills/cv-helper
# Codex
git clone https://github.com/Aliwu-14/cv-helper.git ~/.codex/skills/cv-helper
# OpenClaw
git clone https://github.com/Aliwu-14/cv-helper.git ~/.openclaw/skills/cv-helper
# 通用 Harness
git clone https://github.com/Aliwu-14/cv-helper.git ~/.harness/skills/cv-helper
```

### 跑全部测试

```bash
cd scripts && python -m unittest test_validate_output.py test_validate_section.py \
    test_validate_output_en.py test_validate_section_en.py
```

期望输出：`Ran 88 tests in 1.Xs OK`

## License

本仓库为个人工具，按需要选择合适的开源协议（如 MIT）。