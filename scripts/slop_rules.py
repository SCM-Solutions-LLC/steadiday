"""Phrases that mark copy as machine-written, shared by every script that
writes or checks blog prose.

generate_blog.py lints each new post against these and asks the model to
revise the offending sentences; check_blog_consistency.py fails CI if a
published post still contains one. Keeping the list in one place means the
generator and the check cannot disagree about what counts.

Keep it to patterns that are wrong every time they appear. "really" and
"actually" are slop most of the time, but not always, and a check that
fails on good copy teaches people to ignore it. Those belong in the
generator's prompt, not here.
"""

import re

# (label, pattern). Matched case-insensitively against plain text.
SLOP_PATTERNS = [
    ("em dash", r"—"),
    ("here's the thing / what / why / how", r"\bhere'?s (?:the thing|what|why|how)\b"),
    ("the truth / reality is", r"\bthe (?:truth|reality|real question) is\b"),
    ("it turns out", r"\bit turns out\b"),
    ("let that sink in", r"\blet that sink in\b"),
    ("make no mistake", r"\bmake no mistake\b"),
    ("at the end of the day", r"\bat the end of the day\b"),
    ("in today's world", r"\bin today'?s (?:world|fast-paced|busy)\b"),
    ("when it comes to", r"\bwhen it comes to\b"),
    ("it's worth noting", r"\bit'?s worth (?:noting|mentioning)\b"),
    ("game-changer", r"\bgame[- ]changer\b"),
    ("the bottom line", r"\bthe bottom line\b"),
    ("the good news", r"\bthe good news\b"),
    ("what most people get wrong", r"\bwhat most people (?:get wrong|don'?t (?:know|realize))\b"),
    ("the sweet spot", r"\bthe sweet spot\b"),
    ("not just X, but Y", r"\bnot just\b[^.;:]{1,60}\bbut\b"),
    ("isn't about X. It's about Y", r"\b(?:isn'?t|is not)\s+(?:just\s+)?about\b[^.]{1,80}[.,;]\s*(?:it'?s|it is)\s+about\b"),
    ("leftover length note", r"\(\d+\s*char(?:acter)?s\)"),
    ("genuinely / truly / literally / incredibly",
     r"\b(?:genuinely|truly|literally|incredibly|fundamentally)\b"),
]

_COMPILED = [(label, re.compile(p, re.I)) for label, p in SLOP_PATTERNS]


def plain_text(html):
    """Visible text of an HTML fragment, with tags and entities flattened."""
    from html import unescape
    return unescape(re.sub(r"<[^>]+>", " ", html or ""))


def find_slop(text):
    """[(label, sentence)] for every slop pattern in text, one per sentence."""
    hits = []
    for sentence in re.split(r"(?<=[.!?])\s+", text or ""):
        for label, pattern in _COMPILED:
            if pattern.search(sentence):
                hits.append((label, sentence.strip()))
    return hits
