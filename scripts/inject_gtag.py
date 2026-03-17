#!/usr/bin/env python3
"""
inject_gtag.py — Inject Google Ads conversion tracking tag into all HTML files.

Usage:
    python scripts/inject_gtag.py [directory]

    directory: Root directory to scan for .html files (default: current directory ".")

This script:
  1. Scans all .html files in the given directory (recursively)
  2. Skips files that already have the Google tag installed
  3. Injects the gtag snippet right after the opening <head> tag
  4. Reports what it changed

Safe to run multiple times — it won't double-inject.
"""

import os
import sys
import re

# ── Google Ads Tag ──────────────────────────────────────────────────────────
GTAG_SNIPPET = """<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=AW-17929124014"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'AW-17929124014');
</script>"""

CONVERSION_ID = "AW-17929124014"


def already_has_gtag(html_content):
    """Check if the file already contains the Google tag."""
    return CONVERSION_ID in html_content


def inject_gtag(html_content):
    """Inject the gtag snippet right after the opening <head> tag."""
    # Match <head> or <head ...attributes...>
    pattern = re.compile(r'(<head[^>]*>)', re.IGNORECASE)
    match = pattern.search(html_content)

    if not match:
        return None  # No <head> tag found

    insert_pos = match.end()
    updated = html_content[:insert_pos] + "\n" + GTAG_SNIPPET + "\n" + html_content[insert_pos:]
    return updated


def process_directory(root_dir):
    """Walk through all HTML files and inject the tag."""
    modified = []
    skipped = []
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

                if already_has_gtag(content):
                    skipped.append(filepath)
                    continue

                updated = inject_gtag(content)

                if updated is None:
                    errors.append((filepath, "No <head> tag found"))
                    continue

                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(updated)

                modified.append(filepath)

            except Exception as e:
                errors.append((filepath, str(e)))

    return modified, skipped, errors


def main():
    root_dir = sys.argv[1] if len(sys.argv) > 1 else "."

    if not os.path.isdir(root_dir):
        print(f"Error: '{root_dir}' is not a directory.")
        sys.exit(1)

    print(f"Scanning '{root_dir}' for HTML files...\n")

    modified, skipped, errors = process_directory(root_dir)

    if modified:
        print(f"✅ Injected Google tag into {len(modified)} file(s):")
        for f in modified:
            print(f"   {f}")
    else:
        print("ℹ️  No files needed the Google tag injected.")

    if skipped:
        print(f"\n⏭️  Skipped {len(skipped)} file(s) (already have the tag):")
        for f in skipped:
            print(f"   {f}")

    if errors:
        print(f"\n⚠️  Errors in {len(errors)} file(s):")
        for f, err in errors:
            print(f"   {f}: {err}")

    print("\nDone.")


if __name__ == "__main__":
    main()
