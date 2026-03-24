#!/usr/bin/env python3
"""
apply_tm.py — Apply ™ symbol to SteadiDay brand name across blog files.

Usage:
    python apply_tm.py

Run from the root of your steadiday.com repo.
This updates blog/index.html and scripts/generate_blog.py with the ™ symbol
on user-visible instances of "SteadiDay". SEO tags, RSS, sitemap, and
technical references are left unchanged.
"""

import os
import sys


def apply_replacements(filepath, replacements):
    """Apply a list of (old, new) replacements to a file."""
    if not os.path.exists(filepath):
        print(f"  SKIP: {filepath} not found")
        return 0

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    count = 0
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            count += 1
            print(f"  ✓ Applied: {old[:60]}...")
        else:
            print(f"  ✗ Not found: {old[:60]}...")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    return count


def main():
    print("=" * 50)
    print("SteadiDay™ Brand Update Script")
    print("=" * 50)

    # ── blog/index.html ──────────────────────────────
    print("\n📄 blog/index.html")
    blog_index_changes = [
        # Nav logo span (match with surrounding context to avoid hitting blog card titles)
        (
            '<img src="../assets/icon.jpeg" alt="SteadiDay">\n                <span>SteadiDay</span>',
            '<img src="../assets/icon.jpeg" alt="SteadiDay">\n                <span>SteadiDay™</span>'
        ),
        # Header h1
        (
            '<h1>SteadiDay Blog</h1>',
            '<h1>SteadiDay™ Blog</h1>'
        ),
        # CTA section paragraph
        (
            'SteadiDay helps you manage medications, track your wellness, and build healthy habits',
            'SteadiDay™ helps you manage medications, track your wellness, and build healthy habits'
        ),
        # Footer brand span (match with surrounding context)
        (
            '<img src="../assets/icon.jpeg" alt="SteadiDay">\n                <span>SteadiDay</span>\n            </div>\n            <div class="footer-links">',
            '<img src="../assets/icon.jpeg" alt="SteadiDay">\n                <span>SteadiDay™</span>\n            </div>\n            <div class="footer-links">'
        ),
    ]
    n = apply_replacements("blog/index.html", blog_index_changes)
    print(f"  → {n} changes applied\n")

    # ── scripts/generate_blog.py ─────────────────────
    print("📄 scripts/generate_blog.py")
    generator_changes = [
        # HTML template CTA box paragraph (in get_html_template)
        (
            'SteadiDay helps you manage medications, track your health, and stay connected with loved ones.',
            'SteadiDay™ helps you manage medications, track your health, and stay connected with loved ones.'
        ),
        # Buttondown email - newsletter subscription line
        (
            'SteadiDay Health & Wellness newsletter',
            'SteadiDay™ Health & Wellness newsletter'
        ),
        # Buttondown email - download link text
        (
            'Download SteadiDay free on the App Store',
            'Download SteadiDay™ free on the App Store'
        ),
    ]
    n = apply_replacements("scripts/generate_blog.py", generator_changes)
    print(f"  → {n} changes applied\n")

    print("=" * 50)
    print("Done! Files that do NOT need changes:")
    print("  • blog/rss.xml (XML data format, ™ breaks parsers)")
    print("  • sitemap.xml (URLs only, no brand text)")
    print("  • robots.txt (technical file, no brand text)")
    print("  • Existing blog post HTML files (already published)")
    print("    Future posts will get ™ from the updated template.")
    print("=" * 50)


if __name__ == "__main__":
    main()
