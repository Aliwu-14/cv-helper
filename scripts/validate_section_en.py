#!/usr/bin/env python3
"""Validate non-summary modules of the cv-helper English resume output."""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path

# ── per-module budgets ─────────────────────────────────────────────────────

EXPERIENCE_BULLET_RANGE = (20, 80)
EXPERIENCE_BULLET_HARD_MAX = 100
SKILL_LINE_RANGE = (8, 80)
AWARD_LINE_RANGE = (12, 90)
EDUCATION_LINE_RANGE = (10, 90)

FORBIDDEN_IN_BULLETS = {
    ":": "ASCII colon",
    "—": "em dash",
    "–": "en dash",
}

WEAK_VERBS = (
    "responsible for",
    "participated in",
    "assisted",
    "helped",
    "supported",
    "worked on",
    "dealt with",
    "involved in",
    "some experience in",
    "tried to",
)

# ── helpers ────────────────────────────────────────────────────────────────

def _visible(text: str) -> int:
    return sum(
        1 for c in unicodedata.normalize("NFC", text) if not c.isspace()
    )


STRONG_VERB_LEAD = re.compile(
    r"^\s*[-]?\s*"
    r"(?:led|spokeheaded|drove|coordinated|built|implemented|"
    r"refactored|optimized|deployed|scaled|launched|analyzed|"
    r"designed|created|developed|reduced|grew|increased|automated|"
    r"delivered|executed|shipped|transformed|accelerated|streamlined|"
    r"architected|integrated|managed|orchestrated|pioneered|established|"
    r"restructured|introduced|facilitated|consolidated|generated|curated|"
    r"formulated|devised)"
    r"\b",
    re.I,
)

NUMBER_FRAGMENT = re.compile(
    r"\d+\.?\d*\s*%"
    r"|\d+\.?\d*\s*(?:percent|k\b|m\b|b\b|"
    r"users?|customers?|products?|sessions?|clicks?|"
    r"revenue|gmv|sales|deals|cases|people|teams|months?|weeks?|days?)\b",
    re.I,
)

def _has_anchor(text: str) -> bool:
    scope = re.compile(
        r"\d+\s*(?:teams?|depts?|regions?|countries?|cities?|"
        r"markets?|channels?|customers?|partners?|brands?)\b",
        re.I,
    )
    adoption = re.compile(
        r"(?:adopted|reused|rolled out|deployed across|adopted by)", re.I
    )
    stage = re.compile(
        r"(?:completed|entered|advanced to)\s+"
        r"(?:research|pilot|prototype|development|testing|launch|beta|ga)\b",
        re.I,
    )
    freq = re.compile(
        r"(?:weekly|monthly|quarterly|per sprint|per week|per month|"
        r"\d+\s+(?:times?|iterations?|phases?|cycles?|reports?|demos?))\b",
        re.I,
    )
    return bool(
        scope.search(text)
        or adoption.search(text)
        or stage.search(text)
        or freq.search(text)
    )


# ── error type ─────────────────────────────────────────────────────────────

class SectionError(ValueError):
    """Raised when a resume module violates its structural contract."""


# ── section finder ────────────────────────────────────────────────────────

def _find_section(text: str, heading: str) -> tuple[int, int]:
    """Return (start, end) as 0-based line indices.

    ``start`` is the first non-blank line AFTER the ## heading.
    ``end`` is the 0-based index of the next ## heading line (exclusive).
    If no next ## is found, end = total line count.
    """
    all_lines = text.splitlines()
    heading_pattern = re.compile(rf"^##\s+{re.escape(heading)}\s*$", re.MULTILINE)

    heading_match = heading_pattern.search(text)
    if not heading_match:
        raise SectionError(f"section `## {heading}` not found")

    # heading_match.start() is the char index of '##'
    heading_char = heading_match.start()
    heading_line = text.count("\n", 0, heading_char)

    start = heading_line + 1

    # Find the next ## heading
    remaining_text = text[heading_match.end():]
    next_match = re.search(r"^##\s+", remaining_text, re.MULTILINE)

    if next_match:
        # Point to the newline BEFORE the next ## so end is the line index of that ##
        end_char = heading_match.end() + next_match.start() - 1
        end = text.count("\n", 0, end_char)
    else:
        end = len(all_lines)

    return start, end


# ── per-module validators ──────────────────────────────────────────────────

def _validate_experience_section(text: str, start: int, end: int) -> None:
    all_lines = text.splitlines()
    section_lines = all_lines[start:end]

    # Collect (bullet_start, bullet_end) ranges per sub-header.
    # Only count lines that contain actual bullet content (skip blank lines).
    headers: list[tuple[int, int]] = []
    i = 0
    while i < len(section_lines):
        line = section_lines[i].rstrip()
        if re.match(r"^###\s+", line):
            bullet_start = i + 1
            j = i + 1
            # Skip blank lines after ### until we hit actual bullets
            while j < len(section_lines) and not section_lines[j].strip():
                j += 1
            # Now collect actual bullet lines until next ### or end
            while (
                j < len(section_lines)
                and section_lines[j].strip()
                and not re.match(r"^###", section_lines[j].strip())
            ):
                j += 1
            # Only record if we found at least one bullet line
            if j > bullet_start:
                headers.append((bullet_start, j))
            i = j
        else:
            i += 1

    if not headers:
        raise SectionError(
            "no experience section header found "
            "(expected ### Company | Role | Dates)"
        )

    for bullet_start, bullet_end in headers:
        bullets = []
        for n in range(bullet_start, bullet_end):
            raw = section_lines[n].strip()
            if not raw:
                continue
            stripped = raw.lstrip("-*•").strip()
            if stripped:
                bullets.append(stripped)

        if len(bullets) < 2:
            raise SectionError(
                f"section at line {bullet_start + 1} has {len(bullets)} bullet; "
                "need at least 2"
            )
        if len(bullets) > 4:
            raise SectionError(
                f"section at line {bullet_start + 1} has {len(bullets)} bullets; "
                "trim to 4 or fewer to keep density"
            )
        for idx, body in enumerate(bullets, 1):
            visible = _visible(body)
            if visible < EXPERIENCE_BULLET_RANGE[0]:
                raise SectionError(
                    f"bullet {idx} at section line {bullet_start + 1} has "
                    f"{visible} characters; minimum {EXPERIENCE_BULLET_RANGE[0]}"
                )
            if visible > EXPERIENCE_BULLET_HARD_MAX:
                raise SectionError(
                    f"bullet {idx} at section line {bullet_start + 1} has "
                    f"{visible} characters; hard maximum {EXPERIENCE_BULLET_HARD_MAX}"
                )
            for ch, label in FORBIDDEN_IN_BULLETS.items():
                if ch in body:
                    raise SectionError(
                        f"bullet {idx} at section line {bullet_start + 1} uses "
                        f"'{ch}' ({label}); use plain one-line STAR prose"
                    )
            if not STRONG_VERB_LEAD.match(body):
                lower = body.lower()
                if any(lower.startswith(w) for w in WEAK_VERBS):
                    raise SectionError(
                        f"bullet {idx} at section line {bullet_start + 1} leads "
                        f"with weak verb; use a strong STAR verb"
                    )
            if not NUMBER_FRAGMENT.search(body) and not _has_anchor(body):
                raise SectionError(
                    f"bullet {idx} at section line {bullet_start + 1} lacks a "
                    "quantitative anchor (number, ratio, scope, or adoption signal)"
                )


def _validate_skills_section(text: str, start: int, end: int) -> None:
    all_lines = text.splitlines()
    section_lines = all_lines[start:end]
    bullet_lines = [
        ln.lstrip("-*•").strip()
        for ln in section_lines
        if ln.lstrip("-*•").strip()
    ]
    if len(bullet_lines) < 3:
        raise SectionError(
            f"skills has {len(bullet_lines)} line(s); need at least 3"
        )
    # Check groups FIRST
    required_keywords = ("tool", "language", "method", "framework", "platform")
    found = set()
    for line in bullet_lines:
        lower = line.lower()
        for kw in required_keywords:
            if kw in lower:
                found.add(kw)
    if len(found) < 2:
        raise SectionError(
            f"skills has {len(found)} group(s); need at least 2 groups"
        )
    # Then check per-line length
    for line in bullet_lines:
        visible = _visible(line)
        if visible < SKILL_LINE_RANGE[0]:
            raise SectionError(
                f"skill line '{line[:40]}' has {visible} visible chars; "
                f"minimum {SKILL_LINE_RANGE[0]}"
            )


def _validate_education_section(text: str, start: int, end: int) -> None:
    all_lines = text.splitlines()
    section_lines = all_lines[start:end]
    bullet_lines = [
        ln.lstrip("-*•").strip()
        for ln in section_lines
        if ln.lstrip("-*•").strip()
    ]
    if not bullet_lines:
        raise SectionError("education section is empty")
    for line in bullet_lines:
        if _visible(line) < EDUCATION_LINE_RANGE[0]:
            raise SectionError(
                f"education line is too short (need ≥{EDUCATION_LINE_RANGE[0]} visible chars)"
            )


def _validate_awards_section(text: str, start: int, end: int) -> None:
    all_lines = text.splitlines()
    section_lines = all_lines[start:end]
    bullet_lines = [
        ln.lstrip("-*•").strip()
        for ln in section_lines
        if ln.lstrip("-*•").strip()
    ]
    for line in bullet_lines:
        # Normalize em-dash and en-dash separators so patterns can match
        normalized = line.replace("\u2014", " - ").replace("\u2013", " - ")
        if _visible(normalized) < AWARD_LINE_RANGE[0]:
            raise SectionError(
                f"award line is too short (need ≥{AWARD_LINE_RANGE[0]} visible chars)"
            )
        if not NUMBER_FRAGMENT.search(normalized) and not _has_anchor(normalized):
            raise SectionError(
                f"award line lacks a quantitative anchor "
                "(year, rank, percentile, or top X%)"
            )


# ── public API ────────────────────────────────────────────────────────────

_MODULES = {
    "experience": _validate_experience_section,
    "skills": _validate_skills_section,
    "education": _validate_education_section,
    "awards": _validate_awards_section,
}


def validate_section(text: str, mode: str) -> None:
    """Validate a single module of an English resume.

    Modes: experience | skills | education | awards
    Raises SectionError on violation.
    """
    if mode not in _MODULES:
        raise ValueError(f"unknown mode {mode!r}; choose from {list(_MODULES)}")
    start, end = _find_section(text, mode.capitalize())
    _MODULES[mode](text, start, end)


def _main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate a single non-summary module of a cv-helper English resume. "
            "Modes: experience, skills, education, awards."
        )
    )
    parser.add_argument(
        "--mode",
        choices={"experience", "skills", "education", "awards"},
        required=True,
        help="which section to validate",
    )
    parser.add_argument("file", help="Path to the resume text file")
    args = parser.parse_args()

    path = Path(args.file)
    if not path.is_file():
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        return 1

    text = path.read_text(encoding="utf-8")
    try:
        validate_section(text, args.mode)
    except SectionError as exc:
        print(f"INVALID: {exc}")
        return 1

    print(f"VALID ({args.mode})")
    return 0


if __name__ == "__main__":
    sys.exit(_main())
