#!/usr/bin/env python3
"""Validate the strict four-line output contract for the English resume summary."""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path

# ── character counting ──────────────────────────────────────────────────────

MIN_TOTAL = 240          # total non-space visible characters across all 4 lines
MAX_TOTAL = 380
MAX_LINE = 78            # hard upper bound per line
MIN_LINE = 22            # soft lower bound per line
MAX_WORDS_PER_LINE = 18  # prevents word-bloat

# Patterns that must appear at least once somewhere in the 4-line block.
_REQUIRED_PATTERNS = (
    re.compile(r"\d[%％]"),          # percentage
    re.compile(r"\b(?:led|built|drove|grew|scaled|reduced|launched)\b", re.I),
    re.compile(r"\b(?:SQL|Python|R|JavaScript|Excel|Tableau|Looker)\b", re.I),
)


def _visible(text: str) -> int:
    """Count visible (non-space) characters after NFC normalization."""
    return sum(1 for c in unicodedata.normalize("NFC", text) if not c.isspace())


def _has_number(text: str) -> bool:
    return bool(re.search(r"\d", text))


# ── validators ─────────────────────────────────────────────────────────────

def validate_summary(text: str, check_patterns: bool = True) -> list[str]:
    """Validate an English 4-line summary block; return list of error strings (empty=pass)."""
    errors: list[str] = []
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]

    # Line count
    if len(lines) != 4:
        errors.append(
            f"expected exactly 4 non-empty lines, found {len(lines)}"
        )
        return errors

    # Per-line budgets
    for i, line in enumerate(lines, 1):
        visible = _visible(line)
        if visible < MIN_LINE:
            errors.append(
                f"line {i} has {visible} visible chars; aim for at least {MIN_LINE}"
            )
        if visible > MAX_LINE:
            errors.append(
                f"line {i} has {visible} visible chars; hard upper limit is {MAX_LINE}"
            )
        word_count = len(line.split())
        if word_count > MAX_WORDS_PER_LINE:
            errors.append(
                f"line {i} has {word_count} words; aim for ≤{MAX_WORDS_PER_LINE} "
                "to stay scannable"
            )

    # Total budget
    total = sum(_visible(l) for l in lines)
    if total < MIN_TOTAL:
        errors.append(
            f"total visible chars {total} is below minimum {MIN_TOTAL}"
        )
    if total > MAX_TOTAL:
        errors.append(
            f"total visible chars {total} exceeds hard upper bound {MAX_TOTAL}"
        )

    # Required patterns
    if check_patterns:
        combined = " ".join(lines)
        for pat in _REQUIRED_PATTERNS:
            if not pat.search(combined):
                errors.append(
                    f"summary must include a {pat.pattern!r} signal "
                    "(quantitative anchor, strong STAR verb, or key technical tool)"
                )

    # Weak verbs
    WEAK_PATTERNS = re.compile(
        r"\b(?:responsible for|helped|assisted|involved in|participated in|"
        r"some experience|dealt with|tried to|worked on|familiar with)\b",
        re.I,
    )
    for i, line in enumerate(lines, 1):
        if WEAK_PATTERNS.search(line):
            errors.append(
                f"line {i} uses weak phrasing like '{WEAK_PATTERNS.search(line).group()}'; "
                "use a strong STAR verb (led, built, drove, launched...)"
            )

    # Forbidden characters
    FORBIDDEN_IN_SUMMARY = {":", "："}
    for i, line in enumerate(lines, 1):
        for ch in FORBIDDEN_IN_SUMMARY:
            if ch in line:
                errors.append(
                    f"line {i} contains a colon character; use plain prose instead"
                )

    return errors


# ── CLI ────────────────────────────────────────────────────────────────────

def _main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate an English 4-line summary block for cv-helper."
    )
    parser.add_argument(
        "--mode", choices={"summary", "full"}, default="summary",
        help="summary=first 4 lines; full=validate entire file"
    )
    parser.add_argument("file", help="Path to the resume text file")
    args = parser.parse_args()

    path = Path(args.file)
    if not path.is_file():
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        return 1

    raw = path.read_text(encoding="utf-8")

    if args.mode == "summary":
        lines = [l.strip() for l in raw.strip().splitlines() if l.strip()]
        block = "\n".join(lines[:4])
        errors = validate_summary(block)
    else:
        errors = []
        for i, para in enumerate(raw.split("\n\n"), 1):
            para = para.strip()
            if not para:
                continue
            para_lines = [l.strip() for l in para.splitlines() if l.strip()]
            if len(para_lines) >= 4 and para_lines[0].lower().startswith("summary"):
                errors += [
                    f"[para {i}] {e}" for e in validate_summary("\n".join(para_lines[:4]))
                ]

    if errors:
        print("INVALID:", "; ".join(errors))
        return 1
    print("VALID")
    return 0


if __name__ == "__main__":
    sys.exit(_main())
