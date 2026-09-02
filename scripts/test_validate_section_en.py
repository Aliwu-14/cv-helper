#!/usr/bin/env python3
"""Regression tests for the English section validators (validate_section_en.py)."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from validate_section_en import SectionError, validate_section  # noqa: E402

# Bullets: 20-80 visible chars each.
VALID_EXPERIENCE = """\
## Experience

### Acme Corp | Product Manager | 2023.03 – Present

- Led merchant backend redesign, reducing operation steps by 22% within 6 weeks
- Coordinated 3 engineering squads, increasing release frequency by 35%
- Built funnel monitoring with SQL and Python, delivering 12 weekly reports adopted
- Drove customer segmentation, lifting open rate by 18% across target cohort

### Beacon Consulting | Business Analyst | 2021.06 – 2023.02

- Led competitive benchmark and channel research for FMCG clients, adopted by 3 BUs
- Wrote 6 executive reports, 5 adopted as quarterly strategy material
- Coordinated 22 field staff across 8 cities for market research
- Completed weekly industry newsletter, 12 editions adopted by business
"""


VALID_SKILLS = """\
## Skills

- Tools & Platforms: Figma (proficient), Jira (familiar), GA4 (applied)
- Programming & Query: Python (proficient), SQL (proficient), TypeScript (learning)
- Methods & Frameworks: A/B Testing (familiar), PMO/WBS/RAID (familiar), RAG (familiar)
- Language / Certifications: English CET-6 580, PMP Certified
"""


VALID_EDUCATION = """\
## Education

- Harvard University | Master of Science | Computer Science | 2021.09 – 2023.06
- GPA 3.8/4.0 (top 5%); relevant coursework: Algorithms, Machine Learning
- Thesis: Scalable Recommendation Systems using Graph Neural Networks
"""


VALID_AWARDS = """\
## Awards

- 2024 CFA Level II Pass — CFA Institute — Global Top 35%
- 2023 National Math Modeling Contest — National First Prize — Top 1% (approx 30/30000)
"""


class SectionValidatorTests(unittest.TestCase):
    def test_valid_experience(self) -> None:
        validate_section(VALID_EXPERIENCE, mode="experience")

    def test_valid_skills(self) -> None:
        validate_section(VALID_SKILLS, mode="skills")

    def test_valid_education(self) -> None:
        validate_section(VALID_EDUCATION, mode="education")

    def test_valid_awards(self) -> None:
        validate_section(VALID_AWARDS, mode="awards")

    def test_experience_requires_at_least_two_bullets(self) -> None:
        broken = """\
## Experience

### Acme Corp | Product Manager | 2023.03 – Present

- Led merchant backend redesign, reducing operation steps by 22% within 6 weeks

### Beacon Consulting | Business Analyst | 2021.06 – 2023.02

- Led competitive benchmark research, adopted by 3 BUs
- Wrote 6 executive reports, 5 adopted as quarterly strategy material
"""
        with self.assertRaisesRegex(SectionError, "at least 2"):
            validate_section(broken, mode="experience")

    def test_experience_rejects_weak_verb(self) -> None:
        broken = VALID_EXPERIENCE.replace(
            "Led merchant backend redesign",
            "Responsible for merchant backend redesign",
            1,
        )
        with self.assertRaisesRegex(SectionError, "weak verb"):
            validate_section(broken, mode="experience")

    def test_experience_rejects_no_anchor(self) -> None:
        broken = VALID_EXPERIENCE.replace(
            "Led merchant backend redesign, reducing operation steps by 22% within 6 weeks",
            "Led merchant backend redesign from scratch",
            1,
        )
        with self.assertRaisesRegex(SectionError, "quantitative anchor"):
            validate_section(broken, mode="experience")

    def test_experience_accepts_scope_anchor(self) -> None:
        anchor = VALID_EXPERIENCE.replace(
            "Led merchant backend redesign, reducing operation steps by 22% within 6 weeks",
            "Led merchant backend redesign, coordinating 6 depts and delivering on schedule",
            1,
        )
        validate_section(anchor, mode="experience")

    def test_experience_accepts_adoption_anchor(self) -> None:
        anchor = VALID_EXPERIENCE.replace(
            "Led merchant backend redesign, reducing operation steps by 22% within 6 weeks",
            "Led merchant backend redesign, SOP adopted by team as onboarding template",
            1,
        )
        validate_section(anchor, mode="experience")

    def test_experience_rejects_em_dash(self) -> None:
        broken = VALID_EXPERIENCE.replace(
            "Led merchant backend redesign",
            "Led merchant backend redesign—reducing steps by 22%",
            1,
        )
        with self.assertRaisesRegex(SectionError, "em dash"):
            validate_section(broken, mode="experience")

    def test_experience_rejects_colon(self) -> None:
        broken = VALID_EXPERIENCE.replace(
            "Led merchant backend redesign",
            "Redesign results: led merchant backend redesign",
            1,
        )
        with self.assertRaisesRegex(SectionError, "colon"):
            validate_section(broken, mode="experience")

    def test_experience_rejects_short_bullet(self) -> None:
        broken = VALID_EXPERIENCE.replace(
            "Led merchant backend redesign, reducing operation steps by 22% within 6 weeks",
            "Improved process",
            1,
        )
        with self.assertRaisesRegex(SectionError, "minimum 20"):
            validate_section(broken, mode="experience")

    def test_skills_requires_two_groups(self) -> None:
        # Only 2 lines → triggers "need at least 3" error
        broken = """\
## Skills

- Tools & Platforms: Figma (proficient), Jira (familiar)
- Tools & Platforms: Sketch (proficient), InVision (familiar)

## Awards

- 2024 Best Award - Acme Corp
"""
        with self.assertRaisesRegex(SectionError, "need at least 3"):
            validate_section(broken, mode="skills")
        with self.assertRaisesRegex(SectionError, "need at least 3"):
            validate_section(broken, mode="skills")

    def test_skills_requires_three_lines(self) -> None:
        broken = """\
## Skills

- Tools: Figma (proficient)
- Languages: Python (proficient)
"""
        with self.assertRaisesRegex(SectionError, "need at least 3"):
            validate_section(broken, mode="skills")

    def test_education_rejects_empty(self) -> None:
        with self.assertRaisesRegex(SectionError, "education section is empty"):
            validate_section("## Education\n\n", mode="education")

    def test_awards_anchor_required(self) -> None:
        broken = """\
## Awards

- 2024 Best Employee Award — Acme Corp
"""
        with self.assertRaisesRegex(SectionError, "quantitative anchor"):
            validate_section(broken, mode="awards")


class CliIntegrationTests(unittest.TestCase):
    def _run(self, body: str, *args: str) -> int:
        with tempfile.NamedTemporaryFile(
            "w", suffix=".txt", delete=False, encoding="utf-8"
        ) as handle:
            handle.write(body)
            path = handle.name
        try:
            completed = subprocess.run(
                [sys.executable, str(SCRIPT_DIR / "validate_section_en.py"),
                 *args, path],
                check=False,
                capture_output=True,
                text=True,
            )
            return completed.returncode
        finally:
            Path(path).unlink(missing_ok=True)

    def test_cli_accepts_valid_experience(self) -> None:
        self.assertEqual(
            self._run(VALID_EXPERIENCE, "--mode", "experience"),
            0,
        )

    def test_cli_accepts_valid_skills(self) -> None:
        self.assertEqual(
            self._run(VALID_SKILLS, "--mode", "skills"),
            0,
        )

    def test_cli_rejects_weak_verb(self) -> None:
        broken = VALID_EXPERIENCE.replace(
            "Led merchant backend redesign",
            "Responsible for merchant backend redesign",
            1,
        )
        self.assertNotEqual(
            self._run(broken, "--mode", "experience"),
            0,
        )


if __name__ == "__main__":
    unittest.main()
