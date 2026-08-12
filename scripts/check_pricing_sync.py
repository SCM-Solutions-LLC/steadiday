#!/usr/bin/env python3
"""Fail if the homepage pricing summary drifts from pricing.html.

pricing.html is the source of truth: it carries the full comparison and the
monthly/annual toggle. index.html repeats the headline numbers in a summary
section, and the homepage FAQ states them again in prose. Three copies means
three chances to go stale.

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

PRICE_RE = re.compile(r"\$\d[\d,]*(?:\.\d{2})?")


def section(html, start_marker, end_marker):
    try:
        s = html.index(start_marker)
    except ValueError:
        return None
    e = html.index(end_marker, s) if end_marker in html[s:] else len(html)
    return html[s:e]


def prices_in(text):
    return set(PRICE_RE.findall(text or ""))


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

    print(f"pricing.html prices : {', '.join(sorted(canonical_prices)) or '(none)'}")
    print(f"homepage summary    : {', '.join(sorted(summary_prices)) or '(none)'}")
    print(f"homepage FAQ        : {', '.join(sorted(faq_prices)) or '(none)'}")

    if problems:
        print("\nFAILED:")
        for p in problems:
            print(f"  - {p}")
        print("\npricing.html is the source of truth; update the homepage to match.")
        return 1

    print("\nPASSED: homepage pricing is consistent with pricing.html")
    return 0


if __name__ == "__main__":
    sys.exit(main())
