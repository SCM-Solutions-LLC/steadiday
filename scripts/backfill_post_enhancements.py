#!/usr/bin/env python3
"""
backfill_post_enhancements.py

Apply the v5.7 SEO enhancements to already-published blog posts:

  1. Reviewer line in the article header + reviewedBy / MedicalWebPage
     fields in the Article JSON-LD.
  2. "Related from the SteadiDay Blog" footer block (3 same-category
     posts when possible, falling back to the curated related-category
     graph, then most-recent).
  3. FAQPage JSON-LD synthesized from each post's H2 headings + the
     first paragraph that follows. Only emitted when at least 2 usable
     pairs are extracted — otherwise the post is left without FAQ
     schema rather than shipping a low-quality version.

Idempotent: re-running the script is safe; existing blocks are
detected and skipped. Run from the repo root:

    python3 scripts/backfill_post_enhancements.py
"""

from __future__ import annotations

import os
import re
import sys
from html import escape
from pathlib import Path

# Reuse the live helpers from the generator so the backfill stays
# consistent with what new posts emit.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_blog import (  # noqa: E402
    EDITORIAL_REVIEWER,
    RELATED_POSTS_COUNT,
    build_faq_jsonld,
    pick_related_posts,
    render_related_posts_block,
    _RELATED_CATEGORIES,
)

BLOG_DIR = Path("blog")
INDEX_PATH = BLOG_DIR / "index.html"

# Markers we drop so re-runs detect prior work and skip it.
REVIEWER_MARKER = 'class="article-reviewer"'
RELATED_MARKER = 'class="related-posts"'
FAQ_MARKER = '"@type":"FAQPage"'


def parse_index_categories(index_path: Path) -> dict[str, dict[str, str]]:
    """Return {filename: {"title": ..., "category": ...}} pulled from the
    blog index cards. The index is the only place category survives after
    publish, so it's the source of truth for backfilling related-posts."""
    if not index_path.exists():
        return {}
    content = index_path.read_text(encoding="utf-8")
    cards = re.findall(
        r'<article class="blog-card[^"]*">.*?</article>',
        content,
        re.DOTALL,
    )
    out: dict[str, dict[str, str]] = {}
    for card in cards:
        href_m = re.search(r'href="([^"]+\.html)"', card)
        tag_m = re.search(r'class="blog-card-tag">([^<]+)</span>', card)
        title_m = re.search(r'<h2><a [^>]+>([^<]+)</a></h2>', card)
        if not href_m:
            continue
        fname = href_m.group(1).strip()
        out[fname] = {
            "title": title_m.group(1).strip() if title_m else "",
            "category": tag_m.group(1).strip() if tag_m else "",
        }
    return out


def parse_post(path: Path) -> dict:
    """Extract the fields the backfill needs: title (from <title>),
    h2 list, h1, and the body slice we'll splice into."""
    content = path.read_text(encoding="utf-8")
    title_m = re.search(r'<title>([^<|]+)\s*\|', content)
    title = title_m.group(1).strip() if title_m else path.stem
    date_m = re.match(r'(\d{4}-\d{2}-\d{2})', path.name)
    date = date_m.group(1) if date_m else ""
    return {
        "filename": path.name,
        "title": title,
        "date": date,
        "content": content,
    }


def extract_faqs_from_h2s(content: str, limit: int = 4) -> list[dict]:
    """Heuristic FAQ extraction for posts that pre-date the explicit
    Common Questions section: take each <h2> + the first paragraph
    after it, treat the heading as the question and the paragraph as
    the answer. We only accept headings that already read like
    questions — forcing statement-form H2s into questions produces
    awkward "What about ..." Frankenstein phrasing that hurts more
    than it helps. Posts without question-shaped H2s simply ship
    without FAQ schema; regenerating the post adds it properly."""
    skip_phrases = (
        "bottom line", "the takeaway", "what we know", "what's next",
        "in summary", "summary",
    )
    question_starters = (
        "what", "why", "how", "when", "who", "where", "which",
        "is ", "are ", "should ", "can ", "do ", "does ", "will ",
    )
    pattern = re.compile(
        r'<h2[^>]*>(.*?)</h2>\s*(?:<figure.*?</figure>\s*)?<p[^>]*>(.*?)</p>',
        re.DOTALL | re.IGNORECASE,
    )
    faqs = []
    for h2_html, p_html in pattern.findall(content):
        q = re.sub(r'<[^>]+>', '', h2_html).strip()
        a = re.sub(r'<[^>]+>', '', p_html).strip()
        if not q or not a or len(a) < 40:
            continue
        if any(s in q.lower() for s in skip_phrases):
            continue
        if q.endswith("?"):
            pass
        elif q.lower().startswith(question_starters):
            q = q.rstrip(".:") + "?"
        else:
            # Statement-form heading — skip rather than ship a forced question.
            continue
        faqs.append({"q": q, "a": a})
        if len(faqs) >= limit:
            break
    return faqs


def add_reviewer_to_header(content: str) -> str:
    """Insert the reviewer line inside the article-header just after
    article-meta. Idempotent — no-op if already present."""
    if REVIEWER_MARKER in content:
        return content
    reviewer_html = (
        f'<div class="article-reviewer">Editorially reviewed by '
        f'<a href="{EDITORIAL_REVIEWER["url"]}">{escape(EDITORIAL_REVIEWER["name"])}</a></div>'
    )
    pattern = re.compile(r'(<div class="article-meta">[^<]*</div>)')
    return pattern.sub(r'\1' + reviewer_html, content, count=1)


def add_reviewer_css(content: str) -> str:
    """Append the reviewer + related-posts CSS rules inside the existing
    <style> block if they aren't already there. Idempotent."""
    if ".article-reviewer" in content:
        return content
    extra = (
        "\n        .article-reviewer{font-size:0.9rem;opacity:0.8;font-style:italic;margin-top:0.5rem;}"
        ".article-reviewer a{color:rgba(255,255,255,0.95);text-decoration:underline;}"
        "\n        .related-posts{max-width:750px;margin:2.5rem auto 0;padding:1.75rem 2rem;background:var(--teal-light);border-radius:12px;}"
        "\n        .related-posts h3{margin:0 0 0.75rem;font-size:1.2rem;}.related-posts-list{list-style:none;padding:0;margin:0;}"
        ".related-posts-list li{padding:0.5rem 0;border-bottom:1px solid rgba(30,58,95,0.08);font-size:1rem;}"
        ".related-posts-list li:last-child{border-bottom:none;}"
    )
    return content.replace("</style>", extra + "\n    </style>", 1)


def upgrade_article_jsonld(content: str) -> str:
    """Convert the existing Article JSON-LD into a multi-typed
    MedicalWebPage/Article block with reviewedBy + lastReviewed.
    Idempotent — no-op if MedicalWebPage is already in the JSON-LD."""
    if 'MedicalWebPage' in content:
        return content

    # Find the Article JSON-LD line (it's emitted as one line in the
    # current template, which makes the substitution straightforward).
    pattern = re.compile(
        r'("@type"\s*:\s*)"Article"',
    )
    if not pattern.search(content):
        return content
    content = pattern.sub(r'\1["MedicalWebPage","Article"]', content, count=1)

    reviewer_obj = (
        f'"reviewedBy":{{"@type":"Person",'
        f'"name":"{EDITORIAL_REVIEWER["name"]}",'
        f'"jobTitle":"{EDITORIAL_REVIEWER["jobTitle"]}",'
        f'"url":"{EDITORIAL_REVIEWER["url"]}"}},'
    )
    # Insert reviewedBy + lastReviewed before publisher in the same JSON.
    # The publisher field is present in every post; use it as the anchor.
    date_m = re.search(r'"datePublished"\s*:\s*"([^"]+)"', content)
    iso_date = date_m.group(1) if date_m else ""
    extra = reviewer_obj + (f'"lastReviewed":"{iso_date}",' if iso_date else "")
    content = content.replace('"publisher":', extra + '"publisher":', 1)
    return content


def inject_faq_jsonld(content: str, faqs: list[dict]) -> str:
    """Add a FAQPage JSON-LD <script> after the Article JSON-LD.
    Idempotent — no-op if FAQPage already present."""
    if FAQ_MARKER in content or '"@type": "FAQPage"' in content:
        return content
    block = build_faq_jsonld(faqs)
    if not block:
        return content
    # Insert immediately after the closing </script> of the Article block.
    # The Article JSON-LD is the first ld+json script; key off its closing tag.
    article_close = content.find('</script>', content.find('application/ld+json'))
    if article_close == -1:
        return content
    insert_at = article_close + len('</script>')
    return content[:insert_at] + "\n    " + block + content[insert_at:]


def inject_related_posts(content: str, related_html: str) -> str:
    """Insert the related-posts block immediately before the
    back-to-blog div. Idempotent — no-op if already injected."""
    if not related_html or RELATED_MARKER in content:
        return content
    target = '<div class="back-to-blog">'
    if target not in content:
        return content
    return content.replace(target, related_html + "\n    " + target, 1)


def collect_existing_posts(index_map: dict) -> list[dict]:
    """Build the post-list shape pick_related_posts() expects."""
    posts = []
    for fname, meta in index_map.items():
        if not fname.startswith("20"):
            continue
        date_m = re.match(r'(\d{4}-\d{2}-\d{2})', fname)
        posts.append({
            "filename": fname,
            "title": meta.get("title", ""),
            "category": meta.get("category", ""),
            "slug": re.sub(r'^\d{4}-\d{2}-\d{2}-', '', fname.replace('.html', '')),
            "date": date_m.group(1) if date_m else "",
        })
    posts.sort(key=lambda p: p.get('date', ''), reverse=True)
    return posts


def process_file(path: Path, index_map: dict, existing_posts: list[dict]) -> dict:
    post = parse_post(path)
    original = post["content"]
    content = original

    actions = {"reviewer": False, "related": False, "faq": False, "schema": False}

    if REVIEWER_MARKER not in content:
        content = add_reviewer_css(content)
        content = add_reviewer_to_header(content)
        actions["reviewer"] = True

    if 'MedicalWebPage' not in content:
        content = upgrade_article_jsonld(content)
        actions["schema"] = True

    if FAQ_MARKER not in content:
        faqs = extract_faqs_from_h2s(content)
        if len(faqs) >= 2:
            content = inject_faq_jsonld(content, faqs)
            actions["faq"] = len(faqs)

    if RELATED_MARKER not in content:
        category = index_map.get(path.name, {}).get("category", "")
        related = pick_related_posts(
            category, existing_posts, current_filename=path.name, n=RELATED_POSTS_COUNT,
        )
        related_html = render_related_posts_block(related)
        new_content = inject_related_posts(content, related_html)
        if new_content != content:
            content = new_content
            actions["related"] = len(related)

    if content != original:
        path.write_text(content, encoding="utf-8")
    return actions


def main():
    if not BLOG_DIR.is_dir():
        print(f"❌ {BLOG_DIR} not found — run from repo root.")
        sys.exit(1)

    index_map = parse_index_categories(INDEX_PATH)
    existing_posts = collect_existing_posts(index_map)
    print(f"Loaded category map for {len(index_map)} posts from {INDEX_PATH}")
    print(f"Building related-posts pool from {len(existing_posts)} posts")
    print()

    targets = sorted(
        p for p in BLOG_DIR.glob("*.html")
        if p.name != "index.html"
    )
    totals = {"reviewer": 0, "schema": 0, "faq": 0, "related": 0}
    for path in targets:
        a = process_file(path, index_map, existing_posts)
        if any(a.values()):
            print(f"  [✓] {path.name}: {', '.join(k for k, v in a.items() if v)}")
            for k in totals:
                if a.get(k):
                    totals[k] += 1
        else:
            print(f"  [-] {path.name}: already up to date")

    print()
    print("=" * 60)
    print(f"  reviewer line added: {totals['reviewer']}")
    print(f"  MedicalWebPage / reviewedBy added: {totals['schema']}")
    print(f"  FAQPage schema added: {totals['faq']}")
    print(f"  related-posts block added: {totals['related']}")


if __name__ == "__main__":
    main()
