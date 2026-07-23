from __future__ import annotations

import re
from typing import Any

from ched_ocr.normalize_ocr import normalize_pos_ocr

YEAR_BANNER = re.compile(r"^\s*(FIRST|SECOND|THIRD|FOURTH|FIFTH)\s+YEAR\s*$", re.I)
YEAR_WORD = {"FIRST": 1, "SECOND": 2, "THIRD": 3, "FOURTH": 4, "FIFTH": 5}

SEM_HEADER = re.compile(
    r"(?P<year>\d)(?:st|nd|rd|th)?\s*year\s*[—\-–,]?\s*(?P<sem>\d)(?:st|nd|rd|th)?\s*sem",
    re.I,
)

SKIP_TITLE = re.compile(
    r"^(courses|lec|lab|total|units|prerequisites|psg\b|page\s+\d+|no\.?\s*of\s*hours|"
    r"suggested|sample|program of study|classification|minimum)",
    re.I,
)

# Greedy title, then lec / lab / units (keeps "Calculus 1" intact)
COURSE_LINE_RE = re.compile(
    r"^(?P<title>.+)\s+(?P<lec>\d{1,2})\s+(?P<lab>\d{1,3})\s+(?P<units>\d{1,2})\b(?:\s+(?P<prereq>.+))?$"
)

NUM_LINE_RE = re.compile(
    r"^(?P<lec>\d{1,2})\s+(?P<lab>\d{1,3})\s+(?P<units>\d{1,2})\b(?:\s+(?P<prereq>.+))?$"
)


def _norm_title(title: str) -> str:
    return re.sub(r"\s+", " ", title).strip(" .|-_").replace("\u2019", "'")


def _looks_like_title(title: str) -> bool:
    if len(title) < 3 or len(title) > 120:
        return False
    if SKIP_TITLE.search(title):
        return False
    if title.lower() in {"total", "subtotal", "summary"}:
        return False
    if sum(c.isalpha() for c in title) < 3:
        return False
    return True


def parse_program_of_study(text: str) -> list[dict[str, Any]]:
    text = normalize_pos_ocr(text)
    year_level = 0
    semester = 0
    courses: list[dict[str, Any]] = []
    pending_title: str | None = None

    lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in text.splitlines()]
    lines = [ln for ln in lines if ln and not ln.startswith("#")]

    for ln in lines:
        if ln.startswith("====="):
            continue

        m = YEAR_BANNER.match(ln)
        if m:
            year_level = YEAR_WORD[m.group(1).upper()]
            pending_title = None
            continue

        if "standing" not in ln.lower():
            sm = SEM_HEADER.search(ln)
            if sm:
                year_level = int(sm.group("year"))
                semester = int(sm.group("sem"))
                pending_title = None
                continue

        if re.search(r"No\.?\s*of\s*Hours|Lab/Field|^Lec\b|Prerequisites", ln, re.I):
            continue
        if re.match(r"^TOTAL\b", ln, re.I):
            pending_title = None
            continue

        if not (year_level and semester):
            continue

        cm = COURSE_LINE_RE.match(ln)
        if cm:
            title = _norm_title(cm.group("title"))
            lec, lab, units = int(cm.group("lec")), int(cm.group("lab")), int(cm.group("units"))
            if _looks_like_title(title) and units <= 12 and lec <= 12:
                prereq = re.sub(r"\s+", " ", (cm.group("prereq") or "").strip())
                if prereq.lower() in {"none", "n/a", "-", "—"}:
                    prereq = ""
                courses.append(
                    {
                        "year_level": year_level,
                        "semester": semester,
                        "course_title": title,
                        "lec_hours": lec,
                        "lab_hours": lab,
                        "units": units,
                        "prerequisites": prereq,
                    }
                )
                pending_title = None
                continue

        nm = NUM_LINE_RE.match(ln)
        if nm and pending_title:
            title = _norm_title(pending_title)
            if _looks_like_title(title):
                prereq = re.sub(r"\s+", " ", (nm.group("prereq") or "").strip())
                courses.append(
                    {
                        "year_level": year_level,
                        "semester": semester,
                        "course_title": title,
                        "lec_hours": int(nm.group("lec")),
                        "lab_hours": int(nm.group("lab")),
                        "units": int(nm.group("units")),
                        "prerequisites": prereq,
                    }
                )
            pending_title = None
            continue

        if _looks_like_title(ln) and not re.search(r"\b\d{1,2}\s+\d{1,3}\s+\d{1,2}\b", ln):
            pending_title = f"{pending_title} {ln}" if pending_title and not re.search(r"\d", ln) else ln
            continue

        pending_title = None

    seen: set[tuple] = set()
    uniq: list[dict[str, Any]] = []
    for c in courses:
        key = (c["year_level"], c["semester"], c["course_title"].lower())
        if key in seen:
            continue
        seen.add(key)
        uniq.append(c)
    return uniq
