#!/usr/bin/env python3
"""Fail if the homepage or the on-page assistant drifts from pricing.html.

Covers two kinds of number: the prices, and the free plan's caps - how many
medications, reminders and trusted contacts the free tier allows.

pricing.html is the source of truth: it carries the full comparison and the
monthly/annual toggle. index.html repeats the headline numbers in a summary
section, the homepage FAQ states them again in prose, and the assistant's
knowledge base in steadiday-assistant.js quotes them a fourth time to answer
"how much does it cost". Four copies means four chances to go stale.

The assistant is the copy most likely to be forgotten: it is one JavaScript
file rather than a visible section of a page, so a price change can ship with
the site looking right and the assistant still quoting last quarter's number
to anyone who asks it. The caps have it worse still - three separate answers
state them, so raising the free medication limit means editing three strings
nobody can see from the page.

This is not hypothetical. The page deleted in #33 still advertised a
"Community Phase" in which every feature was free, and listed three features
as included that had since moved to Premium. It had been wrong for a long time
because nothing checked it.

Exits non-zero on a mismatch.
"""

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CANONICAL = ROOT / "pricing.html"
SUMMARY = ROOT / "index.html"
ASSISTANT = ROOT / "steadiday-assistant.js"

PRICE_RE = re.compile(r"\$\d[\d,]*(?:\.\d{2})?")
# The headline figure on a plan card, and the one the monthly/annual toggle
# swaps in. Narrower than PRICE_RE on purpose: a price quoted in prose
# somewhere on pricing.html is not a price we charge for a plan.
PLAN_PRICE_RE = re.compile(r'<span class="amount">(\$[\d,]+(?:\.\d{2})?)</span>')

# The free plan's numeric caps. Prices are not the only figure the assistant
# repeats: it also tells people how many medications, reminders and contacts
# the free plan allows, and those numbers live on the Free card too.
#
# Each noun pattern has to match both the card ("Medication Reminders (up to
# 5)") and the assistant's prose ("up to 5 medications"), which is why the
# "reminder" half is optional. Keep this list short and literal; it is the
# brittle part of this script, and a concept nobody states as a bare number
# does not belong here.
FREE_CAPS = [
    ("medications", r"medication(?:\s+reminder)?s?"),
    # "7 task reminders" on the card and in two answers, but a third says
    # "5 medications and 7 reminders". The lookbehind is what lets the bare
    # form count without "Medication Reminders (up to 5)" reading as the task
    # cap.
    ("task reminders", r"(?<!medication )(?:task\s+)?reminders?"),
    ("trusted contacts", r"trusted\s+contacts?"),
]

# Counts appear as digits on the card and sometimes as words in prose: the
# assistant says "one trusted contact" in one answer and "1 trusted contact"
# in another, and both are good copy.
WORD_NUMBERS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
}
COUNT = r"(\d+|" + "|".join(WORD_NUMBERS) + r")"


def section(html, start_marker, end_marker):
    try:
        s = html.index(start_marker)
    except ValueError:
        return None
    e = html.index(end_marker, s) if end_marker in html[s:] else len(html)
    return html[s:e]


def prices_in(text):
    return set(PRICE_RE.findall(text or ""))


def free_card_features(canonical_body):
    """The Free plan's feature list, one line of plain text per bullet.

    Scoped to the Free card on purpose: "Unlimited Medications" sits on the
    Premium card, and a cap check that read the whole page would compare the
    free limits against it.
    """
    tier = re.search(r'<div class="card-tier">\s*Free\s*</div>', canonical_body)
    if not tier:
        return []
    features = section(canonical_body[tier.end():], '<ul class="card-features"', "</ul>")
    if features is None:
        return []
    return [re.sub(r"<[^>]+>", " ", li) for li in
            re.findall(r"<li>(.*?)</li>", features, re.S)]


def caps_in(texts, noun_re):
    """Every count stated against a noun across these texts.

    Two shapes, both taken from the copy as written: a count immediately
    before the noun ("5 medications", "1 Trusted Contact"), and the
    parenthetical the cards use ("Medication Reminders (up to 5)").

    The count has to sit flush against the noun. Allowing words in between
    would let "5 medications and 7 task reminders" read 5 as the task cap,
    and a check that reports a wrong number is worse than one that reports
    none - the loud failures below cover the case where the copy moves out
    of reach of both shapes.
    """
    before = re.compile(COUNT + r"\s+" + noun_re + r"\b", re.I)
    after = re.compile(noun_re + r"\s*\(\s*up to\s*" + COUNT + r"\s*\)", re.I)
    found = set()
    for text in texts:
        for pattern in (before, after):
            for raw in pattern.findall(text or ""):
                found.add(int(raw) if raw.isdigit() else WORD_NUMBERS[raw.lower()])
    return found


def kb_entries(js):
    """Pull the KB array out of steadiday-assistant.js.

    Regex rather than a JS parser: the array is hand-written with one entry per
    brace at a fixed indent, and the alternative is a Node dependency for CI to
    read three fields. If the file is ever restructured this returns nothing
    and main() fails loudly, which is the point - a drift check that quietly
    matches zero entries is worse than no check.
    """
    try:
        start = js.index("var KB = [")
        end = js.index("\n    ];", start)
    except ValueError:
        return []
    block = js[start:end]
    entries = []
    for body in re.findall(r"^        \{(.*?)^        \}", block, re.S | re.M):
        entries.append({
            "q": field(body, "q"),
            "a": field(body, "a"),
            "link": field(body, "link"),
        })
    return entries


def field(entry_body, name):
    m = re.search(r"\b%s:\s*'((?:[^'\\]|\\.)*)'" % name, entry_body)
    return m.group(1) if m else ""


def main():
    if not CANONICAL.exists() or not SUMMARY.exists():
        print("FAILED: pricing.html or index.html missing")
        return 1

    canonical_html = CANONICAL.read_text(encoding="utf-8")
    summary_html = SUMMARY.read_text(encoding="utf-8")

    # Only look at rendered content, not <style>/<script>.
    canonical_body = canonical_html[canonical_html.index("<body"):]
    canonical_prices = prices_in(canonical_body)

    summary = section(summary_html, '<section class="pricing-summary"', "</section>")
    if summary is None:
        print("FAILED: index.html has no .pricing-summary section.\n"
              "  Either restore it or delete this check.")
        return 1

    problems = []

    summary_prices = prices_in(summary)
    if not summary_prices:
        problems.append("the homepage pricing summary quotes no prices at all")

    unknown = summary_prices - canonical_prices
    if unknown:
        problems.append(
            "price(s) on the homepage that do not appear in pricing.html: "
            + ", ".join(sorted(unknown))
        )

    # The FAQ answer states the same numbers in prose.
    faq = section(summary_html, '<section class="faq-section"', "</section>")
    faq_prices = prices_in(faq)
    faq_unknown = faq_prices - canonical_prices
    if faq_unknown:
        problems.append(
            "price(s) in the homepage FAQ that do not appear in pricing.html: "
            + ", ".join(sorted(faq_unknown))
        )

    # Tier names must line up both ways.
    canonical_tiers = {t.strip().lower() for t in
                       re.findall(r'<div class="card-tier">([^<]+)', canonical_body)}
    summary_tiers = {t.strip().lower() for t in
                     re.findall(r'<div class="plan-tier">([^<]+)', summary)}
    if canonical_tiers and summary_tiers and canonical_tiers != summary_tiers:
        problems.append(
            f"tier names differ - pricing.html has {sorted(canonical_tiers)}, "
            f"homepage has {sorted(summary_tiers)}"
        )

    # The summary must link through rather than trying to be the full page.
    if 'href="pricing.html"' not in summary:
        problems.append("the homepage pricing summary does not link to pricing.html")

    # ---- The assistant's knowledge base ----
    kb_prices = set()
    entries = []
    if not ASSISTANT.exists():
        problems.append(f"{ASSISTANT.name} is missing.\n"
                        "  Either restore it or delete the assistant half of this check.")
    else:
        entries = kb_entries(ASSISTANT.read_text(encoding="utf-8"))
        if not entries:
            problems.append(
                f"no knowledge base entries found in {ASSISTANT.name}.\n"
                "  The KB array moved or changed shape; fix kb_entries() so this\n"
                "  check keeps watching the assistant's prices and caps."
            )
        for entry in entries:
            entry_prices = prices_in(entry["a"])
            if not entry_prices:
                continue
            kb_prices |= entry_prices

            unknown = entry_prices - canonical_prices
            if unknown:
                problems.append(
                    f'the assistant answer "{entry["q"]}" quotes '
                    + ", ".join(sorted(unknown))
                    + ", which does not appear in pricing.html"
                )

            # An answer that states a price owes the reader the full comparison,
            # same rule the homepage summary follows.
            if not entry["link"].startswith("pricing.html"):
                problems.append(
                    f'the assistant answer "{entry["q"]}" quotes a price but links '
                    f'to {entry["link"] or "nothing"} instead of pricing.html'
                )

        # Every price we actually charge has to survive the trip into the
        # assistant. $0 is excluded: the free tier is a card reading "$0" on
        # pricing.html and the words "free forever" in the assistant, and
        # demanding a literal "$0" there would be demanding worse copy.
        chargeable = set(PLAN_PRICE_RE.findall(canonical_body)) - {"$0"}
        if not chargeable:
            problems.append(
                "no plan prices found in pricing.html.\n"
                "  The pricing cards changed shape; fix PLAN_PRICE_RE so this check\n"
                "  keeps noticing prices the assistant has not caught up with."
            )
        forgotten = chargeable - kb_prices
        if forgotten and entries:
            problems.append(
                "price(s) charged on pricing.html that the assistant never mentions: "
                + ", ".join(sorted(forgotten))
                + "\n  Update the KB answers in steadiday-assistant.js to match."
            )

    # ---- The free plan's caps ----
    # Prices are not the only figure the assistant repeats. It also tells
    # people how many medications, reminders and contacts the free plan
    # allows, in three different answers, and those numbers come off the
    # same Free card.
    free_features = free_card_features(canonical_body)
    if not free_features:
        problems.append(
            "no Free plan feature list found in pricing.html.\n"
            "  The pricing cards changed shape; fix free_card_features() so this\n"
            "  check keeps watching the free plan's caps."
        )
    caps_found = []
    for name, noun in FREE_CAPS:
        canonical_caps = caps_in(free_features, noun)
        if len(canonical_caps) != 1:
            if free_features:
                problems.append(
                    f"the Free card gives {len(canonical_caps)} cap(s) for {name}"
                    + (f" ({', '.join(str(n) for n in sorted(canonical_caps))})"
                       if canonical_caps else "")
                    + "; it needs exactly one.\n"
                    "  Fix the card or the FREE_CAPS entry in this script - a cap\n"
                    "  this check cannot pin down is a cap it cannot defend."
                )
            continue
        cap = canonical_caps.pop()
        caps_found.append(f"{name} {cap}")

        said_somewhere = False
        for entry in entries:
            said = caps_in([entry["a"]], noun)
            if not said:
                continue
            said_somewhere = True
            wrong = said - {cap}
            if wrong:
                problems.append(
                    f'the assistant answer "{entry["q"]}" caps {name} at '
                    + ", ".join(str(n) for n in sorted(wrong))
                    + f"; the Free card says {cap}"
                )
        if entries and not said_somewhere:
            problems.append(
                f"the Free card caps {name} at {cap} and no assistant answer "
                "says so.\n"
                "  Either an answer dropped the number or it was reworded out of\n"
                "  reach of FREE_CAPS in this script - widen the pattern there if\n"
                "  the new wording is the wording you want."
            )

    print(f"pricing.html prices : {', '.join(sorted(canonical_prices)) or '(none)'}")
    print(f"homepage summary    : {', '.join(sorted(summary_prices)) or '(none)'}")
    print(f"homepage FAQ        : {', '.join(sorted(faq_prices)) or '(none)'}")
    print(f"assistant KB        : {', '.join(sorted(kb_prices)) or '(none)'}")
    print(f"free plan caps      : {', '.join(caps_found) or '(none)'}")

    if problems:
        print("\nFAILED:")
        for p in problems:
            print(f"  - {p}")
        print("\npricing.html is the source of truth; update the homepage and the\n"
              "assistant knowledge base to match.")
        return 1

    print("\nPASSED: homepage and assistant pricing and caps are consistent with\n"
          "pricing.html")
    return 0


if __name__ == "__main__":
    sys.exit(main())
