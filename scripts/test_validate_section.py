#!/usr/bin/env python3
"""Regression tests for the per-module validators in validate_section.py."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from validate_section import SectionError, validate_section  # noqa: E402


VALID_EXPERIENCE = """\
## 经历（工作 / 实习 / 项目）

### 某 SaaS 公司 | 产品经理 | 2024.03 – 至今

- 主导商家后台改版，从用户访谈到原型上线仅 6 周，关键路径操作步数下降 22%
- 协调 3 个研发小组推进上线验收，月度发布效率提升 35%
- 用神策 + SQL 搭建漏斗监控，每周输出 1 份复盘材料，连续 12 期被业务采纳
- 推动客户分层运营方案落地，分层触达打开率提升 18%

### 某咨询公司 | 商业分析师 | 2023.06 – 2024.02

- 主导快消客户的竞品 Benchmark 与渠道分层调研，方案被 3 个 BU 复用
- 撰写 6 份高管阅读报告，5 份被客户采纳为季度战略材料
- 协调 22 名执行成员，覆盖华北、华东 8 城市场调研
- 完成每周 1 期行业研究简报，连续 12 期被业务侧采纳
"""


VALID_EDUCATION = """\
## 教育背景

- 清华大学 | 硕士 | 管理科学与工程 | 2021.09 – 2024.06
- GPA 3.8/4.0（年级前 5%）；与目标岗位关联的统计、运筹课程各 1 门
"""


VALID_SKILLS = """\
## 技能

- 工具与平台：Figma（熟练）、Jira（熟悉）、神策 / GA4（能够应用）
- 编程语言与查询语言：Python（熟练）、SQL（熟练）、TypeScript（了解边界）
- 方法与框架：PMO / WBS / RAID（熟悉）、A/B Testing（熟悉）、RAG（了解）
- 语言 / 证书：CET-6 550、PMP 已认证、基金从业资格证
"""


VALID_AWARDS = """\
## 奖项与证书

- 2024 CFA Level II 通过 — CFA Institute — 全球前 35% 通过率
- 2023 全国大学生数学建模竞赛 — 国家级一等奖 — Top 1%（约 30/30000）
"""


class SectionValidatorTests(unittest.TestCase):
    def test_valid_experience(self) -> None:
        validate_section(VALID_EXPERIENCE, mode="experience")

    def test_valid_education(self) -> None:
        validate_section(VALID_EDUCATION, mode="education")

    def test_valid_skills(self) -> None:
        validate_section(VALID_SKILLS, mode="skills")

    def test_valid_awards(self) -> None:
        validate_section(VALID_AWARDS, mode="awards")

    def test_experience_requires_blank_line_before_header(self) -> None:
        broken = VALID_EXPERIENCE.replace(
            "## 经历（工作 / 实习 / 项目）\n\n###",
            "## 经历（工作 / 实习 / 项目）\n###",
            1,
        )
        with self.assertRaisesRegex(SectionError, "preceded by a blank line"):
            validate_section(broken, mode="experience")

    def test_experience_rejects_single_bullet(self) -> None:
        broken = """\
## 经历（工作 / 实习 / 项目）

### 某 SaaS 公司 | 产品经理 | 2024.03 – 至今

- 主导商家后台改版，从用户访谈到原型上线仅 6 周，关键路径操作步数下降 22%

### 某咨询公司 | 商业分析师 | 2023.06 – 2024.02

- 主导快消客户的竞品 Benchmark 与渠道分层调研，方案被 3 个 BU 复用
- 撰写 6 份高管阅读报告，5 份被客户采纳为季度战略材料
- 协调 22 名执行成员，覆盖华北、华东 8 城市场调研
- 完成每周 1 期行业研究简报，连续 12 期被业务侧采纳
"""
        with self.assertRaisesRegex(SectionError, "at least 2"):
            validate_section(broken, mode="experience")

    def test_experience_rejects_too_many_bullets(self) -> None:
        broken = VALID_EXPERIENCE + "- 用 SQL 查询自动化 5 张核心表，节省 8h/周人工\n- 输出 1 份 30 页研究报告\n"
        with self.assertRaisesRegex(SectionError, "trim to 4 or fewer"):
            validate_section(broken, mode="experience")

    def test_experience_rejects_short_bullets(self) -> None:
        broken = VALID_EXPERIENCE.replace(
            "主导商家后台改版，从用户访谈到原型上线仅 6 周，关键路径操作步数下降 22%",
            "改版提效",
            1,
        )
        with self.assertRaisesRegex(SectionError, "minimum 20"):
            validate_section(broken, mode="experience")

    def test_experience_rejects_weak_verb(self) -> None:
        broken = VALID_EXPERIENCE.replace(
            "主导商家后台改版",
            "负责商家后台改版",
            1,
        )
        with self.assertRaisesRegex(SectionError, "weak verb"):
            validate_section(broken, mode="experience")

    def test_experience_rejects_no_quantitative_anchor(self) -> None:
        broken = VALID_EXPERIENCE.replace(
            "主导商家后台改版，从用户访谈到原型上线仅 6 周，关键路径操作步数下降 22%",
            "主导商家后台改版，从用户访谈到原型上线一气呵成",
            1,
        )
        with self.assertRaisesRegex(SectionError, "quantitative anchor"):
            validate_section(broken, mode="experience")

    def test_experience_accepts_scope_anchor(self) -> None:
        anchor_only = VALID_EXPERIENCE.replace(
            "主导商家后台改版，从用户访谈到原型上线仅 6 周，关键路径操作步数下降 22%",
            "主导商家后台改版，协调 6 部门对齐需求并按期交付",
            1,
        )
        validate_section(anchor_only, mode="experience")

    def test_experience_accepts_adoption_anchor(self) -> None:
        anchor_only = VALID_EXPERIENCE.replace(
            "主导商家后台改版，从用户访谈到原型上线仅 6 周，关键路径操作步数下降 22%",
            "主导商家后台改版，输出 SOP 被团队沿用为新人入门模板",
            1,
        )
        validate_section(anchor_only, mode="experience")

    def test_experience_accepts_stage_anchor(self) -> None:
        anchor_only = VALID_EXPERIENCE.replace(
            "主导商家后台改版，从用户访谈到原型上线仅 6 周，关键路径操作步数下降 22%",
            "主导商家后台改版，完成用户调研访谈 28 人，原型设计中",
            1,
        )
        validate_section(anchor_only, mode="experience")

    def test_experience_accepts_frequency_anchor(self) -> None:
        anchor_only = VALID_EXPERIENCE.replace(
            "主导商家后台改版，从用户访谈到原型上线仅 6 周，关键路径操作步数下降 22%",
            "主导商家后台改版，每周迭代 1 次，连续 12 周按期交付",
            1,
        )
        validate_section(anchor_only, mode="experience")

    def test_experience_rejects_colon(self) -> None:
        broken = VALID_EXPERIENCE.replace(
            "主导商家后台改版",
            "改版成果：主导商家后台改版",
            1,
        )
        with self.assertRaisesRegex(SectionError, "colon"):
            validate_section(broken, mode="experience")

    def test_experience_rejects_em_dash(self) -> None:
        broken = VALID_EXPERIENCE.replace(
            "主导商家后台改版",
            "主导商家后台改版—操作步数下降 22%",
            1,
        )
        with self.assertRaisesRegex(SectionError, "em dash"):
            validate_section(broken, mode="experience")

    def test_skills_requires_three_groups(self) -> None:
        # Replace the `方法与框架` line with a generic filler to keep line count
        # at 3 but lose the `方法` group required by the validator.
        lines = VALID_SKILLS.splitlines()
        replaced = [
            "- 通用能力：团队协作、文档沉淀与会议组织"
            if "方法与框架" in line else line
            for line in lines
        ]
        broken = "\n".join(replaced)
        with self.assertRaisesRegex(SectionError, "missing required groups"):
            validate_section(broken, mode="skills")

    def test_skills_enforces_minimum_lines(self) -> None:
        broken = """\
## 技能

- 工具与平台：Figma（熟练）
- 编程语言：Python（熟练）
"""
        with self.assertRaisesRegex(SectionError, "need at least 3"):
            validate_section(broken, mode="skills")

    def test_education_rejects_empty(self) -> None:
        with self.assertRaisesRegex(SectionError, "education section is empty"):
            validate_section("## 教育背景\n\n", mode="education")

    def test_awards_section_is_optional(self) -> None:
        # No awards section → success.
        validate_section("## 教育背景\n- 某大学 | 硕士 | CS | 2020 – 2023\n", mode="awards")


class CliIntegrationTests(unittest.TestCase):
    def _run_validator(self, body: str, *args: str) -> int:
        with tempfile.NamedTemporaryFile(
            "w", suffix=".txt", delete=False, encoding="utf-8"
        ) as handle:
            handle.write(body)
            path = handle.name
        try:
            completed = subprocess.run(
                [sys.executable, str(SCRIPT_DIR / "validate_section.py"), *args, path],
                check=False,
                capture_output=True,
                text=True,
            )
            return completed.returncode
        finally:
            os.remove(path)

    def test_cli_accepts_valid_experience(self) -> None:
        self.assertEqual(self._run_validator(VALID_EXPERIENCE, "--mode", "experience"), 0)

    def test_cli_accepts_valid_skills(self) -> None:
        self.assertEqual(self._run_validator(VALID_SKILLS, "--mode", "skills"), 0)

    def test_cli_accepts_valid_education(self) -> None:
        self.assertEqual(self._run_validator(VALID_EDUCATION, "--mode", "education"), 0)

    def test_cli_rejects_weak_verb(self) -> None:
        broken = VALID_EXPERIENCE.replace("主导商家后台改版", "负责商家后台改版", 1)
        self.assertEqual(self._run_validator(broken, "--mode", "experience"), 1)

    def test_cli_rejects_short_bullet(self) -> None:
        broken = VALID_EXPERIENCE.replace(
            "主导商家后台改版，从用户访谈到原型上线仅 6 周，关键路径操作步数下降 22%",
            "改版提效",
            1,
        )
        self.assertEqual(self._run_validator(broken, "--mode", "experience"), 1)


if __name__ == "__main__":
    unittest.main()
