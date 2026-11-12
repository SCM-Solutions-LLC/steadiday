#!/usr/bin/env python3
"""Add the Sources list and JSON-LD citation to already-published posts.

Lists only the external links each post already contains (see
sources_block.py). Posts with no external links are left alone and reported.
Idempotent. Run from the repo root:  python3 scripts/backfill_sources.py
"""
import glob
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sources_block import citation_jsonld, extract_sources, render_sources_block  # noqa: E402

done, none = 0, []
for path in sorted(glob.glob("blog/*.html")):
    if path.endswith("index.html"):
        continue
    s = open(path, encoding="utf-8").read()
    if 'class="post-sources"' in s:
        continue
    start = s.index('class="article-content"')
    end = s.index("</article>", start)
    cta = s.rfind('<div class="cta-box">', start, end)
    # The Sources list goes after the body copy and before the closing CTA.
    insert_at = cta if cta != -1 else s.rfind("</div>", start, end)
    sources = extract_sources(s[start:insert_at])
    if not sources:
        none.append(path)
        continue
    s = s[:insert_at] + render_sources_block(sources) + "\n        " + s[insert_at:]
    # Add citation to the Article JSON-LD (the block that names "Article").
    m = re.search(r'(<script type="application/ld\+json">(?:(?!</script>).)*?"Article"(?:(?!</script>).)*?)("mainEntityOfPage")', s, re.S)
    if not m:
        sys.exit(f"{path}: no Article JSON-LD with mainEntityOfPage; not changed")
    s = s[:m.start(2)] + citation_jsonld(sources) + s[m.start(2):]
    open(path, "w", encoding="utf-8").write(s)
    done += 1

print(f"Sources added to {done} posts.")
if none:
    print("No external links to credit (left unchanged):\n  " + "\n  ".join(none))
