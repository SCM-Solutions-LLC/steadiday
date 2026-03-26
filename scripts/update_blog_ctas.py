#!/usr/bin/env python3
"""
update_blog_ctas.py — Update old blog posts from "waitlist/coming soon" to "download now" messaging.

Usage:
    python scripts/update_blog_ctas.py [directory]

    directory: Root directory to scan for .html files (default: "blog")

This script:
  1. Scans all .html files in the given directory (recursively)
  2. Replaces outdated waitlist/coming-soon/beta language with live app messaging
  3. Updates CTAs to point to the App Store
  4. Reports what it changed

Safe to run multiple times — replacements are idempotent.
"""

import os
import sys
import re

# ── Replacements ────────────────────────────────────────────────────────────
# Each tuple: (pattern, replacement)
# Using re.IGNORECASE for flexibility

REPLACEMENTS = [
    # --- Text replacements (case-insensitive) ---

    # "Join Waitlist Free" / "Join the Waitlist" link text and URLs
    (r'Join\s+the\s+Waitlist\s+Free', 'Download Free on the App Store'),
    (r'Join\s+Waitlist\s+Free', 'Download Free on the App Store'),
    (r'Join\s+the\s+SteadiDay\s+Waitlist', 'Download SteadiDay Free'),
    (r'Join\s+the\s+Waitlist', 'Download Free on the App Store'),
    (r'Join\s+Waitlist', 'Download Free on the App Store'),

    # Waitlist URL -> App Store URL
    (r'https?://(?:www\.)?steadiday\.com/?#waitlist', 'https://apps.apple.com/app/steadiday/id6758526744'),
    (r'href="/?#waitlist"', 'href="https://apps.apple.com/app/steadiday/id6758526744"'),

    # "Coming Soon" status text
    (r'★★★★★\s*Coming\s+Soon', '★★★★★ 5.0 (App Store)'),
    (r'Coming\s+Soon\s+to\s+the\s+App\s+Store', 'Available Now on the App Store'),
    (r'Coming\s+Soon\s+on\s+the\s+App\s+Store', 'Available Now on the App Store'),

    # "Currently in beta" / "launching soon" / "beta" references
    (r'Currently\s+in\s+beta\s*\(launching\s+soon\)', 'Now available on the App Store'),
    (r'Currently\s+in\s+beta', 'Now available on the App Store'),
    (r'currently\s+in\s+beta', 'now available on the App Store'),
    (r'launching\s+soon', 'available now'),

    # Premium pricing references -> everything is free
    (r'Free\s+with\s+Premium\s+at\s+\$3\.99/month\s*\(Safety\s+features\s+always\s+free\)', 'Completely Free — Every Feature Included'),
    (r'Free\s+with\s+Premium\s+at\s+\$3\.99/mo(?:nth)?\s*\(Safety\s+features\s+always\s+free\)', 'Completely Free — Every Feature Included'),
    (r'Free\s+with\s+Premium\s+at\s+\$3\.99/mo(?:nth)?', 'Completely Free — Every Feature Included'),
    (r'\$3\.99/mo(?:nth)?', 'Free'),

    # Comparison table premium price column for SteadiDay
    (r'\$3\.99/mo', 'Free'),

    # "Be the first to try" waitlist messaging
    (r'Be\s+the\s+first\s+to\s+try\s+our', 'Try our'),

    # "Ready to Take Control" CTA section updates (only match old text without "Download free today")
    (r'SteadiDay\s+helps\s+you\s+manage\s+medications[^<]*?all\s+in\s+one\s+simple\s+app\s+designed\s+for\s+adults\s+50\+\.(?!\s*Download\s+free\s+today)',
     'SteadiDay helps you manage medications, track daily tasks, and stay connected with loved ones — all in one simple app designed for adults 50+. Download free today.'),

    # Generic "sign up" / "get notified" language
    (r'Sign\s+up\s+to\s+be\s+notified\s+when\s+SteadiDay\s+launches', 'Download SteadiDay free from the App Store'),
    (r'Get\s+notified\s+when\s+SteadiDay\s+launches', 'Download SteadiDay free from the App Store'),
    (r'when\s+SteadiDay\s+launches', 'and try SteadiDay free'),
    (r'when\s+we\s+launch', 'today'),
]


def update_content(html_content):
    """Apply all replacements to the HTML content."""
    updated = html_content
    changes = []

    for pattern, replacement in REPLACEMENTS:
        new_content = re.sub(pattern, replacement, updated, flags=re.IGNORECASE | re.DOTALL)
        if new_content != updated:
            changes.append(pattern)
            updated = new_content

    return updated, changes


def process_directory(root_dir):
    """Walk through all HTML files and apply updates."""
    modified = []
    unchanged = []
    errors = []

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip hidden directories and node_modules
        dirnames[:] = [d for d in dirnames if not d.startswith('.') and d != 'node_modules']

        for filename in filenames:
            if not filename.endswith('.html'):
                continue

            filepath = os.path.join(dirpath, filename)

            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                updated, changes = update_content(content)

                if changes:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(updated)
                    modified.append((filepath, changes))
                else:
                    unchanged.append(filepath)

            except Exception as e:
                errors.append((filepath, str(e)))

    return modified, unchanged, errors


def main():
    root_dir = sys.argv[1] if len(sys.argv) > 1 else "blog"

    if not os.path.isdir(root_dir):
        print(f"Error: '{root_dir}' is not a directory.")
        sys.exit(1)

    print(f"Scanning {root_dir} for outdated blog CTAs...\n")

    modified, unchanged, errors = process_directory(root_dir)

    if modified:
        print(f"✅ Updated {len(modified)} file(s):\n")
        for filepath, changes in modified:
            print(f"  📝 {filepath}")
            for pattern in changes:
                # Show a readable version of the pattern
                readable = pattern.replace(r'\s+', ' ').replace(r'\s*', ' ')
                readable = readable[:60]
                print(f"      → matched: {readable}...")
            print()
    else:
        print("ℹ️  No files needed updating.\n")

    if unchanged:
        print(f"⏭️  {len(unchanged)} file(s) already up to date.")

    if errors:
        print(f"\n❌ {len(errors)} error(s):")
        for filepath, error in errors:
            print(f"  {filepath}: {error}")


if __name__ == "__main__":
    main()
