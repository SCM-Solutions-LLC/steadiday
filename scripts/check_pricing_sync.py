#!/usr/bin/env python3
"""Fail if the homepage or the on-page assistant drifts from pricing.html.

pricing.html is the source of truth: it carries the full comparison and the
monthly/annual toggle. index.html repeats the headline numbers in a summary
section, the homepage FAQ states them again in prose, and the assistant's
knowledge base in steadiday-assistant.js quotes them a fourth time to answer
"how much does it cost". Four copies means four chances to go stale.

The assistant is the copy most likely to be forgotten: it is one JavaScript
file rather than a visible section of a page, so a price change can ship with
the site looking right and the assistant still quoting last quarter's number
to anyone who asks it.

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


def section(html, start_marker, end_marker):
    try:
        s = html.index(start_marker)
    except ValueError:
        return None
    e = html.index(end_marker, s) if end_marker in html[s:] else len(html)
    return html[s:e]


def prices_in(text):
    return set(PRICE_RE.findall(text or ""))


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
    if not ASSISTANT.exists():
        problems.append(f"{ASSISTANT.name} is missing.\n"
                        "  Either restore it or delete the assistant half of this check.")
    else:
        entries = kb_entries(ASSISTANT.read_text(encoding="utf-8"))
        if not entries:
            problems.append(
                f"no knowledge base entries found in {ASSISTANT.name}.\n"
                "  The KB array moved or changed shape; fix kb_entries() so this\n"
                "  check keeps watching the assistant's prices."
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

    print(f"pricing.html prices : {', '.join(sorted(canonical_prices)) or '(none)'}")
    print(f"homepage summary    : {', '.join(sorted(summary_prices)) or '(none)'}")
    print(f"homepage FAQ        : {', '.join(sorted(faq_prices)) or '(none)'}")
    print(f"assistant KB        : {', '.join(sorted(kb_prices)) or '(none)'}")

    if problems:
        print("\nFAILED:")
        for p in problems:
            print(f"  - {p}")
        print("\npricing.html is the source of truth; update the homepage and the\n"
              "assistant knowledge base to match.")
        return 1

    print("\nPASSED: homepage and assistant pricing are consistent with pricing.html")
    return 0


if __name__ == "__main__":
    sys.exit(main())
