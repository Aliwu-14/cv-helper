# cv-helper

> 中文简历定制生成器。基于候选人履历、目标岗位 JD 与公司最新公开信息，为整份中文简历输出 ATS 友好、可被 HR 快速理解的定制版内容。

## 功能概览

| 模块 | 说明 |
|------|------|
| `references/patterns.md` | 能力型表述模式库，提供 STAR 压缩骨架、能力任务链、自然能力语言与编辑规则 |
| `references/interview_prep.md` | 简历 → 面试预测问题库（STAR 通用模板 + 经历追问链 + 职能专项问题） |
| `references/templates.md` | LaTeX / Marp / HTML 三套简历导出模板代码 |
| `scripts/validate_output.py` | 中文四行总结校验器（CLI：`python validate_output.py resume.txt`） |
| `scripts/validate_section.py` | 中文非总结模块校验器（CLI：`python validate_section.py --mode experience resume.txt`） |
| `scripts/validate_output_en.py` | 英文四行总结校验器 |
| `scripts/validate_section_en.py` | 英文非总结模块校验器 |
| `scripts/test_*.py` | 校验器回归测试套件（共 88 个测试） |

## 快速开始

```bash
# 校验中文四行总结
python scripts/validate_output.py <resume.txt>

# 校验中文经历模块
python scripts/validate_section.py --mode experience <resume.txt>

# 跑全部测试
cd scripts && python -m unittest test_validate_output.py test_validate_section.py \
    test_validate_output_en.py test_validate_section_en.py
```

## License

本仓库为个人工具，按需要选择合适的开源协议（如 MIT）。