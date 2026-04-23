#!/usr/bin/env python3
"""
SteadiDay Blog Post Migrator v1.1
Updates existing blog posts with topic-relevant images using Claude + Unsplash search.

Usage:
  python scripts/update_existing_posts.py                    # Dry run
  python scripts/update_existing_posts.py --apply            # Apply all changes
  python scripts/update_existing_posts.py --apply --no-api   # Skip API, CSS + video only

Requires: ANTHROPIC_API_KEY environment variable (for image search)
          pip install anthropic
"""
import os, re, sys, glob, json, random, time, urllib.request

BLOG_DIR = "blog"
LAYOUT_PATTERNS = [
    ["full","float-right","full","float-left","full"],
    ["float-right","full","float-left","full","float-right"],
    ["float-left","float-right","full","float-left","full"],
    ["full","float-left","float-right","full","float-left"],
    ["float-right","float-left","full","float-right","full"],
]
DYNAMIC_CSS = """
        .article-image.float-left { float: left; width: 45%; margin: 0.5rem 1.5rem 1rem 0; }
        .article-image.float-right { float: right; width: 45%; margin: 0.5rem 0 1rem 1.5rem; }
        .article-image.full { width: 100%; float: none; clear: both; }
        .article-content h2 { clear: both; }
        @media (max-width: 768px) { .article-image.float-left, .article-image.float-right { float: none; width: 100%; margin: 2rem 0; } }"""

_used_heroes = set()
_used_inlines = set()
_client = None

def get_client():
    global _client
    if _client is None:
        import anthropic
        _client = anthropic.Anthropic()
    return _client

def call_api(prompt, use_search=True, max_retries=5):
    from anthropic import APIStatusError
    client = get_client()
    tools = [{"type":"web_search_20250305","name":"web_search"}] if use_search else []
    for attempt in range(max_retries):
        try:
            msg = client.messages.create(model="claude-sonnet-4-6", max_tokens=1000,
                tools=tools, messages=[{"role":"user","content":prompt}])
            return "".join(b.text for b in msg.content if hasattr(b,'text'))
        except APIStatusError as e:
            if e.status_code in (429,529) or e.status_code >= 500:
                delay = 30 * (2**attempt)
                print(f"      API {e.status_code}, retry in {delay}s...")
                time.sleep(delay)
            else:
                print(f"      API error: {e}"); return None
        except Exception as e:
            print(f"      API error: {e}"); return None
    return None

def search_topic_images(title, count=6):
    global _used_inlines
    prompt = f"""Find {count} Unsplash photos SPECIFICALLY relevant to this blog topic:
"{title}"

The images should visually represent the ACTUAL subject matter:
- "Dental Care" -> smiling people, dental visits, healthy teeth, toothbrushes
- "Heart Guidelines" -> heart health, blood pressure, cardiovascular
- "Brain Training" -> puzzles, learning, mental focus
- "Joint Pain" -> gentle movement, hands, physical therapy
- "Medication Tips" -> pill organizers, pharmacy, doctor consultation
- "Sleep Tips" -> peaceful bedroom, nighttime routine

Do NOT return generic yoga/nature/meditation unless the topic IS about that.

Requirements: from images.unsplash.com, varied, warm/positive, for adults 50+
Format: https://images.unsplash.com/photo-XXXXX?w=800&q=80

Return ONLY JSON: [{{"url":"...","alt":"Description relevant to {title}"}}] or NONE"""
    response = call_api(prompt, use_search=True)
    if not response or "NONE" in response: return None
    try:
        m = re.search(r'\[[\s\S]*?\]', response)
        if m:
            imgs = json.loads(m.group())
            valid = [i for i in imgs if isinstance(i,dict) and "url" in i and "alt" in i
                     and "unsplash.com" in i["url"] and i["url"] not in _used_inlines]
            if valid:
                for i in valid: _used_inlines.add(i["url"])
                return valid
    except: pass
    return None

def search_hero(title):
    global _used_heroes
    prompt = f"""Find ONE high-quality Unsplash photo for the hero banner of: "{title}"
It should visually represent the topic (NOT generic nature/yoga unless the topic IS that).
Wide/landscape orientation, warm, inviting, for adults 50+.
Format: https://images.unsplash.com/photo-XXXXX?w=1200&q=80
Return ONLY the URL or NONE."""
    response = call_api(prompt, use_search=True)
    if not response or "NONE" in response: return None
    m = re.search(r'https://images\.unsplash\.com/photo-[^\s"\']+', response)
    if m:
        url = m.group(0)
        if url not in _used_heroes:
            _used_heroes.add(url); return url
    return None

def verify_video(vid_id):
    try:
        req = urllib.request.Request(
            f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={vid_id}&format=json",
            headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r: return r.status == 200
    except urllib.error.HTTPError: return False
    except: return True

def extract_info(html):
    title = ""
    m = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL)
    if m: title = re.sub(r'<[^>]+>','',m.group(1)).strip()
    hero_m = re.search(r'<img\s+src="([^"]+)"[^>]*class="hero-image"', html)
    hero_url = hero_m.group(1) if hero_m else ""
    inline_count = len(re.findall(r'<figure class="article-image', html))
    videos = re.findall(r'youtube-nocookie\.com/embed/([a-zA-Z0-9_-]+)', html)
    return {"title":title,"hero_url":hero_url,"inline_count":inline_count,"video_ids":videos}

def inject_css(html):
    if ".article-image.float-left" in html: return html, False
    html = html.replace("</style>", DYNAMIC_CSS + "\n    </style>")
    return html, True

def replace_hero(html, new_url):
    m = re.search(r'<img\s+src="([^"]+)"[^>]*class="hero-image"', html)
    if m:
        old = m.group(1)
        html = html.replace(old, new_url)
        return html, old
    return html, None

def replace_inlines(html, new_images):
    pat = r'<figure class="article-image[^"]*">\s*<img[^>]+>\s*<figcaption>[^<]*</figcaption>\s*</figure>'
    figs = list(re.finditer(pat, html))
    if not figs or not new_images: return html, 0
    layout = random.choice(LAYOUT_PATTERNS)
    n = 0
    for i in range(len(figs)-1,-1,-1):
        match = figs[i]
        if i >= len(new_images): continue
        img = new_images[i]
        lc = layout[i % len(layout)]
        cls = "article-image" if lc == "full" else f"article-image {lc}"
        fig = f'<figure class="{cls}"><img src="{img["url"]}" alt="{img["alt"]}" loading="lazy"><figcaption>{img["alt"]}</figcaption></figure>'
        html = html[:match.start()] + fig + html[match.end():]
        n += 1
    return html, n

def apply_layouts_only(html):
    """Apply varied layout classes without changing images."""
    figs = list(re.finditer(r'<figure class="article-image">', html))
    if not figs: return html, False
    layout = random.choice(LAYOUT_PATTERNS)
    for i in range(len(figs)-1,-1,-1):
        m = figs[i]
        lc = layout[i % len(layout)]
        if lc != "full":
            html = html[:m.start()] + f'<figure class="article-image {lc}">' + html[m.end():]
    return html, True

def process_post(filepath, apply=False, use_api=True):
    filename = os.path.basename(filepath)
    changes = []
    with open(filepath,'r',encoding='utf-8') as f: html = f.read()
    original = html
    info = extract_info(html)
    if not info["title"]: return [f"Could not extract title"]

    # CSS
    html, css_ok = inject_css(html)
    if css_ok: changes.append("Added layout CSS")

    if use_api:
        # Hero
        print(f"      Hero search: {info['title'][:45]}...")
        new_hero = search_hero(info["title"])
        if new_hero:
            html, old = replace_hero(html, new_hero)
            if old: changes.append(f"Hero: new topic-specific image")
        else:
            changes.append("Hero: kept (no better match)")

        # Inlines
        if info["inline_count"] > 0:
            print(f"      Inline search ({info['inline_count']} images)...")
            new_imgs = search_topic_images(info["title"], count=info["inline_count"]+1)
            if new_imgs:
                html, n = replace_inlines(html, new_imgs)
                if n: changes.append(f"Replaced {n} inlines (topic-specific + varied layout)")
            else:
                html, ok = apply_layouts_only(html)
                if ok: changes.append("Applied varied layouts to existing images")

        time.sleep(2)
    else:
        html, ok = apply_layouts_only(html)
        if ok: changes.append("Applied varied layouts")

    # Videos
    for vid in info["video_ids"]:
        if not verify_video(vid): changes.append(f"⚠ Broken video: {vid}")

    if apply and html != original:
        with open(filepath,'w',encoding='utf-8') as f: f.write(html)

    return changes

def refresh_index(apply=False, use_api=True):
    path = os.path.join(BLOG_DIR,"index.html")
    if not os.path.exists(path): print("  Index not found"); return
    with open(path,'r',encoding='utf-8') as f: content = f.read()

    # Collect all cards: find title + image pairs
    # The index has: background-image url, then later <h2><a>Title</a></h2>
    cards = re.findall(r"background-image: url\('([^']+)'\).*?<h2><a[^>]*>(.*?)</a>", content, re.DOTALL)
    if not cards: print("  No cards found"); return

    changes = 0
    for old_url, raw_title in cards:
        title = re.sub(r'<[^>]+>','',raw_title).strip()
        if not title or not use_api: continue
        print(f"    Thumb: {title[:40]}...")
        new_url = search_hero(title)
        if new_url:
            new_url = new_url.replace("w=1200","w=800")
            content = content.replace(old_url, new_url, 1)
            changes += 1
            time.sleep(2)

    if changes > 0 and apply:
        with open(path,'w',encoding='utf-8') as f: f.write(content)
    print(f"  Thumbnails: {changes} updated" + (" (applied)" if apply else " (dry run)"))

def main():
    apply = "--apply" in sys.argv
    use_api = "--no-api" not in sys.argv

    print("="*60)
    print("SteadiDay Blog Migrator v1.1")
    print("="*60)
    print(f"Mode: {'APPLY' if apply else 'DRY RUN'}")

    if use_api:
        if not os.environ.get("ANTHROPIC_API_KEY"):
            print("⚠ ANTHROPIC_API_KEY not set. Use --no-api for CSS-only mode.")
            use_api = False
        else:
            print("API: ON (topic-specific image search)")
    else:
        print("API: OFF (CSS + video only)")
    print()

    posts = sorted([f for f in glob.glob(os.path.join(BLOG_DIR,"*.html"))
                    if os.path.basename(f) != "index.html"
                    and os.path.getsize(f) >= 1024], reverse=True)

    print(f"Found {len(posts)} posts\n")
    if not posts: print("No posts. Run from repo root."); sys.exit(1)

    total = warnings = 0
    for fp in posts:
        fn = os.path.basename(fp)
        print(f"  {fn}")
        changes = process_post(fp, apply=apply, use_api=use_api)
        for c in changes:
            icon = "⚠" if c.startswith("⚠") else ("✅" if apply else "📝")
            print(f"    {icon} {c}")
            if c.startswith("⚠"): warnings += 1
        total += len(changes)

    print(f"\nRefreshing index thumbnails...")
    refresh_index(apply=apply, use_api=use_api)

    print(f"\n{'='*60}")
    print(f"Total: {total} changes, {warnings} warnings")
    if not apply: print("DRY RUN. Use --apply to save.")
    else: print("Done. Review: git diff blog/")
    print("="*60)

if __name__ == "__main__":
    main()
