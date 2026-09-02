#!/usr/bin/env python3
"""Validate non-summary modules of the cv-helper full resume output."""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path

# Per-line visible-character budgets for each resume module.
EDUCATION_LINE_RANGE = (10, 90)  # generous: covers school + degree + major + dates + 1-2 short notes
EXPERIENCE_BULLET_RANGE = (20, 75)
EXPERIENCE_BULLET_HARD_MAX = 95  # anything beyond this is treated as a summary, not a bullet
SKILL_LINE_RANGE = (8, 80)
AWARD_LINE_RANGE = (12, 90)

FORBIDDEN_PUNCTUATION_IN_BULLETS = {
    ":": "ASCII colon",
    "：": "Chinese colon",
    "—": "em dash",
    "–": "en dash",
}

WEAK_VERBS = (
    "负责",
    "参与",
    "协助",
    "帮助",
    "跟进",
    "了解",
    "涉及",
    "处理",
    "支持",
)


SECTION_HEADER = re.compile(
    r"^###\s+(?P<head>.+?)\s*[|｜]\s*(?P<role>.+?)\s*[|｜]\s*(?P<period>.+?)\s*$"
)
SECTION_HEADER_PROJECT = re.compile(
    r"^###\s+(?P<head>.+?)\s*[|｜]\s*(?P<period>.+?)\s*$"
)
BULLET_PATTERN = re.compile(r"^\s*[-•●]\s+(?P<body>.+?)\s*$")
EDUCATION_LINE_PATTERN = re.compile(r"^\s*-\s+(?P<body>.+?)\s*$")
SKILL_LINE_PATTERN = re.compile(r"^\s*-\s+(?P<body>.+?)\s*$")
AWARD_LINE_PATTERN = re.compile(r"^\s*-\s+(?P<body>.+?)\s*$")
NUMBER_FRAGMENT = re.compile(r"\d+(?:[.,]\d+)?\s*(?:%|‰|人|个|条|分|倍|x|X|岁|天|日|周|月|季度|季|年|小时|分钟|秒|ms|k|K|M|G|万|亿|TB|GB|MB|KB)?")
STRONG_VERB_LEAD = re.compile(
    r"^\s*[-\u2014\u2013\u2022\u00B7]?\s*"
    r"(?:主导|牵头|推动|协调|推进|落地|搭建|实现|重构|优化|治理|集成|部署|拆解|提炼|沉淀|复盘|评估|论证|洞察|投放|增长|留存|唤醒|维系|自动化|调研|原型|上线|验证|迭代|撰写|产出|对齐|辅导|反馈|汇报|桥接|立项|制定|承担|输出|整理|完成|覆盖|引入|落地|组建|运营|优化|对接|识别|追踪|分析|构建|接入|编写|转化|调优|建立|管理|训练|建模|开源|迁移|提升|加速|整合|攻克|压缩|缩短|降低|削减|扩容|扩量|规划|推行|赛选|打磨|把关|扩展|驱动|预测|识别|诊断|调度|输送|管理|整理|统筹|把控|加速|深化|萃取|建模)"
)


FIRST_VERB_PATTERN = re.compile(r"^([\u4e00-\u9fff]+)")


class SectionError(ValueError):
    """Raised when a single module violates the skill contract."""


def visible_length(text: str) -> int:
    normalized = unicodedata.normalize("NFC", text)
    return sum(not character.isspace() for character in normalized)


def _require_blank_between(text: str, header_index: int) -> None:
    """Each `###` header must be preceded by a blank line in the resume body."""
    lines = text.splitlines()
    if header_index == 0:
        return
    if lines[header_index - 1].strip() != "":
        raise SectionError(
            f"section header at line {header_index + 1} must be preceded by a blank line"
        )


def _validate_experience_section(body: str, *, start: int, end: int) -> None:
    """Validate an `## 经历` block: must contain at least one header + 2-4 bullets per header."""
    lines = body.splitlines()[start:end]
    sections: list[tuple[int, list[str]]] = []
    current_bullets: list[str] = []
    current_header: int | None = None

    for offset, line in enumerate(lines):
        if SECTION_HEADER.match(line) or SECTION_HEADER_PROJECT.match(line):
            if current_header is not None and not current_bullets:
                raise SectionError(
                    f"section at line {current_header + 1} has no bullets; "
                    "each experience section needs 2-4 STAR-style bullets"
                )
            if current_header is not None:
                sections.append((current_header, current_bullets))
            current_header = start + offset
            current_bullets = []
            _require_blank_between(body, current_header)
            continue
        match = BULLET_PATTERN.match(line)
        if match:
            if current_header is None:
                raise SectionError(
                    f"bullet at line {start + offset + 1} appears before any section header"
                )
            current_bullets.append(match.group("body"))
    if current_header is None:
        raise SectionError("experience section has no `###` header")
    if current_header is not None:
        if not current_bullets:
            raise SectionError(
                f"section at line {current_header + 1} has no bullets; "
                "each experience section needs 2-4 STAR-style bullets"
            )
        sections.append((current_header, current_bullets))

    for header_line, bullets in sections:
        if len(bullets) < 2:
            raise SectionError(
                f"section at line {header_line + 1} has {len(bullets)} bullet; "
                "need at least 2"
            )
        if len(bullets) > 4:
            raise SectionError(
                f"section at line {header_line + 1} has {len(bullets)} bullets; "
                "trim to 4 or fewer to keep density"
            )
        for index, body_text in enumerate(bullets, start=1):
            if not STRONG_VERB_LEAD.match("-" + body_text):
                first_verb_match = FIRST_VERB_PATTERN.match(body_text)
                first_segment = first_verb_match.group(1) if first_verb_match else ""
                # Prefer long-form strong verbs in the segment if present;
                # otherwise fall back to the leading one or two characters.
                candidates = []
                if first_segment:
                    candidates.append(first_segment)
                    for length in (3, 2, 1):
                        if len(first_segment) >= length:
                            candidates.append(first_segment[:length])
                weak_hit = next((c for c in candidates if c in WEAK_VERBS), None)
                if weak_hit:
                    raise SectionError(
                        f"bullet {index} at section line {header_line + 1} leads "
                        f"with weak verb '{weak_hit}'; use a strong STAR verb"
                    )
            count = visible_length(body_text)
            if count < EXPERIENCE_BULLET_RANGE[0]:
                raise SectionError(
                    f"bullet {index} at section line {header_line + 1} has "
                    f"{count} characters; minimum {EXPERIENCE_BULLET_RANGE[0]}"
                )
            if count > EXPERIENCE_BULLET_HARD_MAX:
                raise SectionError(
                    f"bullet {index} at section line {header_line + 1} has "
                    f"{count} characters; hard maximum {EXPERIENCE_BULLET_HARD_MAX}"
                )
            for punctuation, label in FORBIDDEN_PUNCTUATION_IN_BULLETS.items():
                if punctuation in body_text:
                    raise SectionError(
                        f"bullet {index} at section line {header_line + 1} uses "
                        f"{label}; bullets should be one-line STAR-compressed sentences"
                    )
            if not NUMBER_FRAGMENT.search(body_text) and not _has_quantitative_anchor(body_text):
                raise SectionError(
                    f"bullet {index} at section line {header_line + 1} lacks a "
                    "quantitative anchor (number, ratio, scope, or adoption signal)"
                )


def _has_quantitative_anchor(text: str) -> bool:
    """Allow scope / adoption / stage anchors when absolute numbers are missing."""
    scope_patterns = (
        r"\d+\s*(?:部门|团队|城市|城|国|BU|业务线|客户|厂商|渠道|门店)",
        r"(?:覆盖|横跨|跨)\s*\d+",
    )
    adoption_patterns = (
        r"(?:被|纳入|设为|成为|沿用).{0,16}(?:标准|模板|路线图|复用)",
        r"采纳",
    )
    stage_patterns = (
        r"(?:完成|进入|推进至).{0,16}(?:调研|访谈|原型|开发|测试|灰度|上线|验证)阶段",
        r"第\s*[一二三四五六七八九十0-9]+\s*(?:期|阶段|周|月)",
    )
    frequency_patterns = (
        r"(?:连续|累计)?\s*\d+\s*(?:期|周|月|天|单|次|条|篇)",
        r"周度|月度|季度|每日|每周",
    )
    joined = (
        r"|".join(scope_patterns + adoption_patterns + stage_patterns + frequency_patterns)
    )
    return re.search(joined, text) is not None


def _validate_simple_bulleted_block(
    text: str,
    *,
    start: int,
    end: int,
    line_range: tuple[int, int],
    label: str,
    min_lines: int,
    max_lines: int,
    required_groups: tuple[str, ...] = (),
) -> None:
    """Validate a bulleted module: each `- ` line is checked for length and (optionally) group coverage."""
    lines = [line for line in text.splitlines()[start:end] if line.strip()]
    if not lines:
        raise SectionError(f"{label} section is empty")
    bullets = []
    for raw in lines:
        pattern = (
            EDUCATION_LINE_PATTERN
            if label == "education"
            else SKILL_LINE_PATTERN
            if label == "skills"
            else AWARD_LINE_PATTERN
        )
        match = pattern.match(raw)
        if not match:
            raise SectionError(f"{label} line is not bulleted: {raw[:60]}")
        bullets.append(match.group("body"))
    if len(bullets) < min_lines:
        raise SectionError(
            f"{label} has {len(bullets)} line(s); need at least {min_lines}"
        )
    if len(bullets) > max_lines:
        raise SectionError(
            f"{label} has {len(bullets)} lines; trim to {max_lines} or fewer"
        )
    for index, body_text in enumerate(bullets, start=1):
        count = visible_length(body_text)
        if count < line_range[0]:
            raise SectionError(
                f"{label} line {index} has {count} characters; minimum {line_range[0]}"
            )
        if count > line_range[1]:
            raise SectionError(
                f"{label} line {index} has {count} characters; maximum {line_range[1]}"
            )
    if required_groups:
        groups_present = set()
        for body_text in bullets:
            for group in required_groups:
                if group in body_text:
                    groups_present.add(group)
        missing = [g for g in required_groups if g not in groups_present]
        if missing:
            raise SectionError(
                f"{label} is missing required groups: {', '.join(missing)}"
            )


def _find_section(text: str, heading: str) -> tuple[int, int]:
    """Return the (start_line, end_line) of a section delimited by a Markdown `## heading`.

    The returned ``start_line`` is the 0-indexed line index of the first line AFTER the
    ``##`` heading; the returned ``end_line`` is the 0-indexed line index of the next
    ``##`` heading (or the end of the buffer).
    """
    pattern = re.compile(rf"^##\s+{re.escape(heading)}\s*$", re.MULTILINE)
    match = pattern.search(text)
    if not match:
        raise SectionError(f"section `## {heading}` not found")
    heading_line = text.count("\n", 0, match.start())
    start = heading_line + 1
    next_heading = re.search(r"^##\s+", text[match.end():], re.MULTILINE)
    if next_heading:
        end_match_start = match.end() + next_heading.start()
        end_line = text.count("\n", 0, end_match_start)
    else:
        end_line = text.count("\n", 0, len(text))
    return start, end_line


def validate_section(text: str, mode: str) -> None:
    normalized = unicodedata.normalize("NFC", text)
    if mode == "experience":
        start, end = _find_section(normalized, "经历（工作 / 实习 / 项目）")
        # fall back to several alternative heading spellings
        if end <= start:
            for alt in ("经历", "工作经历"):
                try:
                    start, end = _find_section(normalized, alt)
                    break
                except SectionError:
                    continue
        _validate_experience_section(normalized, start=start, end=end)
    elif mode == "education":
        # heading candidates
        for candidate in ("教育背景", "教育"):
            try:
                start, end = _find_section(normalized, candidate)
                break
            except SectionError:
                start, end = -1, -1
        if start < 0:
            raise SectionError("education section not found")
        _validate_simple_bulleted_block(
            normalized,
            start=start,
            end=end,
            line_range=EDUCATION_LINE_RANGE,
            label="education",
            min_lines=1,
            max_lines=6,
        )
    elif mode == "skills":
        for candidate in ("技能",):
            try:
                start, end = _find_section(normalized, candidate)
                break
            except SectionError:
                start, end = -1, -1
        if start < 0:
            raise SectionError("skills section not found")
        _validate_simple_bulleted_block(
            normalized,
            start=start,
            end=end,
            line_range=SKILL_LINE_RANGE,
            label="skills",
            min_lines=3,
            max_lines=8,
            required_groups=("工具", "语言", "方法"),
        )
    elif mode == "awards":
        for candidate in ("奖项与证书", "奖项", "证书"):
            try:
                start, end = _find_section(normalized, candidate)
                break
            except SectionError:
                start, end = -1, -1
        if start < 0:
            # Awards section is optional; treat empty as pass.
            return
        _validate_simple_bulleted_block(
            normalized,
            start=start,
            end=end,
            line_range=AWARD_LINE_RANGE,
            label="awards",
            min_lines=1,
            max_lines=10,
        )
    else:
        raise SectionError(f"unsupported mode: {mode}")


def read_text(input_path: str | None) -> str:
    if input_path in (None, "-"):
        return sys.stdin.read()
    return Path(input_path).read_text(encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate a single non-summary module of a cv-helper full resume. "
            "Modes: education, experience, skills, awards. "
            "Pass '-' or omit the path to read from stdin."
        )
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="UTF-8 text file to validate; omit or use '-' to read stdin.",
    )
    parser.add_argument(
        "--mode",
        required=True,
        choices=("education", "experience", "skills", "awards"),
        help="Which module to validate.",
    )
    args = parser.parse_args()

    try:
        validate_section(read_text(args.input), args.mode)
    except (OSError, UnicodeError, SectionError) as error:
        print(f"INVALID: {error}", file=sys.stderr)
        return 1

    print(f"VALID ({args.mode})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
