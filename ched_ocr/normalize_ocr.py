from __future__ import annotations

import re

REPLACEMENTS: list[tuple[str, str]] = [
    (r"(?im)^\s*list year\s*[—\-–]?\s*1[%*!\"'lI°]?\s*sem\w*", "1st year — 1st semester"),
    (r"(?im)^\s*\[?ist year\s*[—\-–]?\s*2[\"'!%]?\s*sem\w*", "1st year — 2nd semester"),
    (r"(?im)^\s*it year\s*[—\-–]?\s*1[%*!\"'lI°]?\s*sem\w*", "1st year — 1st semester"),
    (r"(?im)^\s*2[\"'!]?4?\s*year\s*[—\-–]?\s*1[%*]?\s*sem\w*", "2nd year — 1st semester"),
    (r"(?im)^\s*2[nd\"'!]*\s*year\s*[—\-–]?\s*2[\"'!nd%]?\s*sem\w*", "2nd year — 2nd semester"),
    (r"(?im)^\s*[83][rd\"'!]*\s*year\s*[—\-–]?\s*1[%*]?\s*sem\w*", "3rd year — 1st semester"),
    (r"(?im)^\s*[83][rd\"'!]*\s*year\s*[—\-–]?\s*2[\"'!%]?\s*sem\w*", "3rd year — 2nd semester"),
    (r"(?im)^\s*4(?:th)?\s*year\s*[—\-–]?\s*1[%*]?\s*sem\w*", "4th year — 1st semester"),
    (r"(?im)^\s*(?:GE|Br)\s*year\s*[—\-–]?\s*2[\"'!%]?\s*sem\w*", "4th year — 2nd semester"),
    (r"(?im)^\s*4(?:th)?\s*year\s*[—\-–]?\s*2[\"'!%]?\s*sem\w*", "4th year — 2nd semester"),
    (r"(?im)Calculus\s+4(\s+\d+\s+\d+\s+\d+)", r"Calculus 1\1"),
]


def normalize_pos_ocr(text: str) -> str:
    out = text
    for pat, repl in REPLACEMENTS:
        out = re.sub(pat, repl, out)
    return out
