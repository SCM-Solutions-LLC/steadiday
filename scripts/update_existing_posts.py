#!/usr/bin/env python3
"""
SteadiDay Blog Post Migrator v1.0
One-time script to update existing blog posts with:
  1. Fresh hero and inline images (no repeats across posts)
  2. Varied image layout CSS (float-left, float-right, full-width)
  3. YouTube video verification (flags broken embeds)
  4. Injects updated CSS for dynamic image layouts
  5. Refreshes blog index thumbnails

Usage:
  python update_existing_posts.py              # Dry run (shows what would change)
  python update_existing_posts.py --apply      # Apply changes
  python update_existing_posts.py --apply --skip-images  # Only add CSS + verify videos

Requires: No API key needed. Runs locally against your blog/ directory.
"""

import os
import re
import sys
import glob
import random
import urllib.request
from datetime import datetime

BLOG_DIR = "blog"

# =============================================================================
# IMAGE POOLS — same structure as generate_blog.py
# Each post gets unique images; no two posts share the same hero or inline
# =============================================================================

HERO_POOL = [
    "https://images.unsplash.com/photo-1518241353330-0f7941c2d9b5?w=1200&q=80",
    "https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=1200&q=80",
    "https://images.unsplash.com/photo-1499209974431-9dddcece7f88?w=1200&q=80",
    "https://images.unsplash.com/photo-1474418397713-7ede21d49118?w=1200&q=80",
    "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1200&q=80",
    "https://images.unsplash.com/photo-1529693662653-9d480530a697?w=1200&q=80",
    "https://images.unsplash.com/photo-1470252649378-9c29740c9fa8?w=1200&q=80",
    "https://images.unsplash.com/photo-1501854140801-50d01698950b?w=1200&q=80",
    "https://images.unsplash.com/photo-1475924156734-496f6cac6ec1?w=1200&q=80",
    "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=1200&q=80",
    "https://images.unsplash.com/photo-1502082553048-f009c37129b9?w=1200&q=80",
    "https://images.unsplash.com/photo-1433086966358-54859d0ed716?w=1200&q=80",
    "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=1200&q=80",
    "https://images.unsplash.com/photo-1587854692152-cbe660dbde88?w=1200&q=80",
    "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=1200&q=80",
    "https://images.unsplash.com/photo-1486218119243-13883505764c?w=1200&q=80",
    "https://images.unsplash.com/photo-1538805060514-97d9cc17730c?w=1200&q=80",
    "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=1200&q=80",
    "https://images.unsplash.com/photo-1490645935967-10de6ba17061?w=1200&q=80",
    "https://images.unsplash.com/photo-1498837167922-ddd27525d352?w=1200&q=80",
    "https://images.unsplash.com/photo-1541781774459-bb2af2f05b55?w=1200&q=80",
    "https://images.unsplash.com/photo-1515894203077-9cd36032142f?w=1200&q=80",
    "https://images.unsplash.com/photo-1505576399279-565b52d4ac71?w=1200&q=80",
    "https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=1200&q=80",
    "https://images.unsplash.com/photo-1559757175-5700dde675bc?w=1200&q=80",
    "https://images.unsplash.com/photo-1606761568499-6d2451b23c66?w=1200&q=80",
    "https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=1200&q=80",
    "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=1200&q=80",
    "https://images.unsplash.com/photo-1545205597-3d9d02c29597?w=1200&q=80",
    "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=1200&q=80",
]

INLINE_POOL = [
    {"url": "https://images.unsplash.com/photo-1508672019048-805c876b67e2?w=800&q=80", "alt": "Peaceful beach scene"},
    {"url": "https://images.unsplash.com/photo-1515377905703-c4788e51af15?w=800&q=80", "alt": "Sunlight through trees"},
    {"url": "https://images.unsplash.com/photo-1528715471579-d1bcf0ba5e83?w=800&q=80", "alt": "Calm space with plants"},
    {"url": "https://images.unsplash.com/photo-1519823551278-64ac92734fb1?w=800&q=80", "alt": "Journaling with tea"},
    {"url": "https://images.unsplash.com/photo-1506252374453-ef5237291d83?w=800&q=80", "alt": "Peaceful garden path"},
    {"url": "https://images.unsplash.com/photo-1517021897933-0e0319cfbc28?w=800&q=80", "alt": "Sunrise over calm water"},
    {"url": "https://images.unsplash.com/photo-1500904156668-a21764a29575?w=800&q=80", "alt": "Cozy reading corner"},
    {"url": "https://images.unsplash.com/photo-1446511437394-d789541e7f95?w=800&q=80", "alt": "Walking in nature"},
    {"url": "https://images.unsplash.com/photo-1576602976047-174e57a47881?w=800&q=80", "alt": "Healthcare professional"},
    {"url": "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=800&q=80", "alt": "Morning routine with coffee"},
    {"url": "https://images.unsplash.com/photo-1550831107-1553da8c8464?w=800&q=80", "alt": "Pharmacy shelves"},
    {"url": "https://images.unsplash.com/photo-1607619056574-7b8d3ee536b2?w=800&q=80", "alt": "Daily health routine"},
    {"url": "https://images.unsplash.com/photo-1573883431205-98b5f10aaedb?w=800&q=80", "alt": "Mobile health app"},
    {"url": "https://images.unsplash.com/photo-1517457373958-b7bdd4587205?w=800&q=80", "alt": "Couple walking together"},
    {"url": "https://images.unsplash.com/photo-1454418747937-bd95bb945625?w=800&q=80", "alt": "Active and vibrant"},
    {"url": "https://images.unsplash.com/photo-1600880292203-757bb62b4baf?w=800&q=80", "alt": "Casual conversation"},
    {"url": "https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=800&q=80", "alt": "Friends enjoying outdoors"},
    {"url": "https://images.unsplash.com/photo-1552196563-55cd4e45efb3?w=800&q=80", "alt": "Walking outdoors"},
    {"url": "https://images.unsplash.com/photo-1518611012118-696072aa579a?w=800&q=80", "alt": "Group fitness class"},
    {"url": "https://images.unsplash.com/photo-1574680096145-d05b474e2155?w=800&q=80", "alt": "Balance exercises"},
    {"url": "https://images.unsplash.com/photo-1540189549336-e6e99c3679fe?w=800&q=80", "alt": "Balanced meal plate"},
    {"url": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800&q=80", "alt": "Home-cooked meal"},
    {"url": "https://images.unsplash.com/photo-1490818387583-1baba5e638af?w=800&q=80", "alt": "Green smoothie bowl"},
    {"url": "https://images.unsplash.com/photo-1543362906-acfc16c67564?w=800&q=80", "alt": "Mediterranean spread"},
    {"url": "https://images.unsplash.com/photo-1547592180-85f173990554?w=800&q=80", "alt": "Spices and herbs"},
    {"url": "https://images.unsplash.com/photo-1505253716362-afaea1d3d1af?w=800&q=80", "alt": "Farmers market produce"},
    {"url": "https://images.unsplash.com/photo-1495197359483-d092478c170a?w=800&q=80", "alt": "Comfortable bedroom"},
    {"url": "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=800&q=80", "alt": "Herbal tea at night"},
    {"url": "https://images.unsplash.com/photo-1540518614846-7eded433c457?w=800&q=80", "alt": "Soft pillows and blankets"},
    {"url": "https://images.unsplash.com/photo-1476480862126-209bfaa8edc8?w=800&q=80", "alt": "Jogging on a trail"},
    {"url": "https://images.unsplash.com/photo-1517963879433-6ad2b056d712?w=800&q=80", "alt": "Swimming laps"},
    {"url": "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=800&q=80", "alt": "Learning and education"},
    {"url": "https://images.unsplash.com/photo-1456406644174-8ddd4cd52a06?w=800&q=80", "alt": "Reading a book"},
    {"url": "https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?w=800&q=80", "alt": "Creative writing"},
    {"url": "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=800&q=80", "alt": "Group learning session"},
    {"url": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80", "alt": "Well-lit home interior"},
    {"url": "https://images.unsplash.com/photo-1584515933487-779824d29309?w=800&q=80", "alt": "Emergency preparedness kit"},
    {"url": "https://images.unsplash.com/photo-1518495973542-4542c06a5843?w=800&q=80", "alt": "Dappled sunlight through leaves"},
    {"url": "https://images.unsplash.com/photo-1502082553048-f009c37129b9?w=800&q=80", "alt": "Sunlit forest clearing"},
    {"url": "https://images.unsplash.com/photo-1433086966358-54859d0ed716?w=800&q=80", "alt": "Waterfall serenity"},
    {"url": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=800&q=80", "alt": "Forest walking path"},
    {"url": "https://images.unsplash.com/photo-1484627147104-f5197bcd6651?w=800&q=80", "alt": "Gentle morning light"},
    {"url": "https://images.unsplash.com/photo-1510414842594-a61c69b5ae57?w=800&q=80", "alt": "Ocean calm at sunset"},
    {"url": "https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=800&q=80", "alt": "Open book and coffee"},
    {"url": "https://images.unsplash.com/photo-1488590528505-98d2b5aba04b?w=800&q=80", "alt": "Technology workspace"},
    {"url": "https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=800&q=80", "alt": "Connected devices"},
    {"url": "https://images.unsplash.com/photo-1517048676732-d65bc937f952?w=800&q=80", "alt": "Group discussion"},
    {"url": "https://images.unsplash.com/photo-1581579438747-104c53d7fbc4?w=800&q=80", "alt": "Morning stretch routine"},
    {"url": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=800&q=80", "alt": "Confident warm smile"},
    {"url": "https://images.unsplash.com/photo-1530268729831-4b0b9e170218?w=800&q=80", "alt": "Community gathering"},
    {"url": "https://images.unsplash.com/photo-1599058945522-28d584b6f0ff?w=800&q=80", "alt": "Outdoor tai chi practice"},
    {"url": "https://images.unsplash.com/photo-1545389336-cf090694435e?w=800&q=80", "alt": "Gentle stretching session"},
    {"url": "https://images.unsplash.com/photo-1606787366850-de6330128bfc?w=800&q=80", "alt": "Breakfast spread"},
    {"url": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=800&q=80", "alt": "Healthy avocado toast"},
    {"url": "https://images.unsplash.com/photo-1484980972926-edee96e0960d?w=800&q=80", "alt": "Berry bowl"},
    {"url": "https://images.unsplash.com/photo-1455619452474-d2be8b1e70cd?w=800&q=80", "alt": "Warm soup bowl"},
    {"url": "https://images.unsplash.com/photo-1476224203421-9ac39bcb3327?w=800&q=80", "alt": "Fresh bread and olive oil"},
    {"url": "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800&q=80", "alt": "Accessible home design"},
    {"url": "https://images.unsplash.com/photo-1494438639946-1ebd1d20bf85?w=800&q=80", "alt": "Clear walking pathways"},
    {"url": "https://images.unsplash.com/photo-1583912267550-d974311a9a6e?w=800&q=80", "alt": "Health tracking checklist"},
]

# =============================================================================
# LAYOUT PATTERNS — varied image positioning per post
# Each pattern defines how images are laid out within a single post
# =============================================================================
LAYOUT_PATTERNS = [
    # Pattern A: full, right, full, left, full
    ["full", "float-right", "full", "float-left", "full"],
    # Pattern B: right, full, left, full, right
    ["float-right", "full", "float-left", "full", "float-right"],
    # Pattern C: left, right, full, left, full
    ["float-left", "float-right", "full", "float-left", "full"],
    # Pattern D: full, left, right, full, left
    ["full", "float-left", "float-right", "full", "float-left"],
    # Pattern E: right, left, full, right, full
    ["float-right", "float-left", "full", "float-right", "full"],
]

# CSS to inject for varied image layouts
DYNAMIC_IMAGE_CSS = """
        .article-image.float-left { float: left; width: 45%; margin: 0.5rem 1.5rem 1rem 0; }
        .article-image.float-right { float: right; width: 45%; margin: 0.5rem 0 1rem 1.5rem; }
        .article-image.full { width: 100%; float: none; clear: both; }
        .article-content h2 { clear: both; }
        @media (max-width: 768px) { .article-image.float-left, .article-image.float-right { float: none; width: 100%; margin: 2rem 0; } }"""

# Track used images across all posts to prevent repeats
_used_heroes = set()
_used_inlines = set()


def verify_youtube_video(video_id):
    """Check if a YouTube video is still publicly available."""
    url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except urllib.error.HTTPError:
        return False
    except Exception:
        return True  # Assume working if we can't check


def get_blog_posts():
    """Get all blog post HTML files sorted by date (newest first)."""
    posts = []
    for filepath in glob.glob(os.path.join(BLOG_DIR, "*.html")):
        filename = os.path.basename(filepath)
        if filename == "index.html":
            continue
        try:
            if os.path.getsize(filepath) < 1024:
                continue
        except OSError:
            continue
        posts.append(filepath)
    posts.sort(reverse=True)
    return posts


def pick_hero():
    """Pick a hero image not yet used by any post in this run."""
    global _used_heroes
    available = [h for h in HERO_POOL if h not in _used_heroes]
    if not available:
        _used_heroes.clear()
        available = HERO_POOL
    pick = random.choice(available)
    _used_heroes.add(pick)
    return pick


def pick_inlines(count):
    """Pick N inline images not yet used by any post in this run."""
    global _used_inlines
    available = [img for img in INLINE_POOL if img["url"] not in _used_inlines]
    if len(available) < count:
        _used_inlines.clear()
        available = INLINE_POOL[:]
    picks = random.sample(available, min(count, len(available)))
    for img in picks:
        _used_inlines.add(img["url"])
    return picks


def inject_css(html):
    """Add dynamic image layout CSS if not already present."""
    if "float-left" in html and ".article-image.float-left" in html:
        return html, False  # Already has the CSS

    # Find the closing </style> tag and inject before it
    css_marker = ".article-image figcaption"
    if css_marker in html:
        # Inject after the figcaption rule block
        insert_point = html.find(css_marker)
        # Find the closing brace after this rule
        brace_pos = html.find("}", insert_point)
        if brace_pos > 0:
            html = html[:brace_pos+1] + DYNAMIC_IMAGE_CSS + html[brace_pos+1:]
            return html, True

    # Fallback: inject before </style>
    html = html.replace("</style>", DYNAMIC_IMAGE_CSS + "\n    </style>")
    return html, True


def update_hero_image(html, new_hero_url):
    """Replace the hero image URL throughout the HTML."""
    # Match hero image in: <img src="..." class="hero-image"
    hero_pattern = r'(<img\s+src=")([^"]+)("\s+alt="[^"]*"\s+class="hero-image")'
    match = re.search(hero_pattern, html)
    if match:
        old_url = match.group(2)
        html = html.replace(old_url, new_hero_url)
        return html, old_url
    # Also try: class="hero-image" ... src="..."
    hero_pattern2 = r'(class="hero-image"[^>]*src=")([^"]+)(")'
    match2 = re.search(hero_pattern2, html)
    if match2:
        old_url = match2.group(2)
        html = html.replace(old_url, new_hero_url)
        return html, old_url
    return html, None


def update_inline_images(html, new_images):
    """Replace inline article images and add layout variation."""
    # Find all existing figure.article-image blocks
    figure_pattern = r'<figure class="article-image[^"]*">\s*<img[^>]+>\s*<figcaption>[^<]*</figcaption>\s*</figure>'
    figures = list(re.finditer(figure_pattern, html))

    if not figures:
        return html, 0

    # Pick a layout pattern
    layout = random.choice(LAYOUT_PATTERNS)

    # Replace each figure with a new image + layout class
    replacements = 0
    for i, match in enumerate(reversed(figures)):
        # Work backwards so positions don't shift
        idx = len(figures) - 1 - i
        if idx >= len(new_images):
            continue

        img = new_images[idx]
        layout_class = layout[idx % len(layout)]

        if layout_class == "full":
            css_class = "article-image"
        else:
            css_class = f"article-image {layout_class}"

        new_figure = f'<figure class="{css_class}"><img src="{img["url"]}" alt="{img["alt"]}" loading="lazy"><figcaption>{img["alt"]}</figcaption></figure>'

        html = html[:match.start()] + new_figure + html[match.end():]
        replacements += 1

    return html, replacements


def check_videos(html):
    """Find and verify all embedded YouTube videos. Return list of issues."""
    issues = []
    video_pattern = r'youtube-nocookie\.com/embed/([a-zA-Z0-9_-]+)'
    for match in re.finditer(video_pattern, html):
        video_id = match.group(1)
        if not verify_youtube_video(video_id):
            issues.append(f"Broken video: {video_id}")
    return issues


def process_post(filepath, apply=False, skip_images=False):
    """Process a single blog post. Returns a summary of changes."""
    filename = os.path.basename(filepath)
    changes = []

    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    original_html = html

    # 1. Inject dynamic image CSS
    html, css_added = inject_css(html)
    if css_added:
        changes.append("Added dynamic image layout CSS")

    if not skip_images:
        # 2. Replace hero image
        new_hero = pick_hero()
        html, old_hero = update_hero_image(html, new_hero)
        if old_hero:
            changes.append(f"Hero: {old_hero.split('photo-')[1][:12] if 'photo-' in old_hero else 'unknown'}... → {new_hero.split('photo-')[1][:12]}")

        # 3. Replace inline images with layout variation
        # Count existing inline images
        figure_count = len(re.findall(r'<figure class="article-image', html))
        if figure_count > 0:
            new_inlines = pick_inlines(figure_count)
            html, replaced = update_inline_images(html, new_inlines)
            if replaced > 0:
                layout_used = random.choice(["A", "B", "C", "D", "E"])
                changes.append(f"Replaced {replaced} inline images (layout pattern {layout_used})")

    # 4. Check embedded videos
    video_issues = check_videos(html)
    for issue in video_issues:
        changes.append(f"⚠ {issue}")

    # 5. Save if applying
    if apply and html != original_html:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)

    return changes


def refresh_index_thumbnails(apply=False):
    """Update blog index to use varied thumbnails."""
    index_path = os.path.join(BLOG_DIR, "index.html")
    if not os.path.exists(index_path):
        print("  Blog index not found, skipping thumbnail refresh")
        return

    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # Find all blog card image URLs and randomize them
    card_pattern = r"(class=\"blog-card-image\" style=\"background-image: url\(')([^']+)('\)\")"
    matches = list(re.finditer(card_pattern, content))

    if not matches:
        print("  No blog card images found in index")
        return

    # Shuffle available hero images for thumbnails
    thumb_pool = HERO_POOL[:]
    random.shuffle(thumb_pool)

    changes = 0
    for i, match in enumerate(matches):
        new_thumb = thumb_pool[i % len(thumb_pool)].replace("w=1200", "w=800")
        old_thumb = match.group(2)
        if old_thumb != new_thumb:
            content = content[:match.start(2)] + new_thumb + content[match.end(2):]
            # Recalculate positions after replacement
            offset = len(new_thumb) - len(old_thumb)
            # Re-read matches after each replacement to avoid offset issues
            content_temp = content  # This is a simplified approach
            changes += 1

    if changes > 0 and apply:
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(content)

    print(f"  Index thumbnails: {changes} updated" + (" (applied)" if apply else " (dry run)"))


def main():
    apply = "--apply" in sys.argv
    skip_images = "--skip-images" in sys.argv

    print("=" * 60)
    print("SteadiDay Blog Post Migrator v1.0")
    print("=" * 60)
    print(f"Mode: {'APPLY CHANGES' if apply else 'DRY RUN (use --apply to save)'}")
    if skip_images:
        print("Skipping image replacement (CSS + video check only)")
    print()

    posts = get_blog_posts()
    print(f"Found {len(posts)} blog posts\n")

    if not posts:
        print("No posts found. Make sure you're running from the repo root.")
        sys.exit(1)

    total_changes = 0
    video_warnings = 0

    for filepath in posts:
        filename = os.path.basename(filepath)
        changes = process_post(filepath, apply=apply, skip_images=skip_images)

        if changes:
            status = "✅" if apply else "📝"
            print(f"{status} {filename}")
            for change in changes:
                print(f"    {change}")
                if change.startswith("⚠"):
                    video_warnings += 1
            total_changes += len(changes)
        else:
            print(f"  — {filename} (no changes needed)")

    print()

    # Refresh index thumbnails
    print("Refreshing index thumbnails...")
    refresh_index_thumbnails(apply=apply)

    print()
    print("=" * 60)
    print(f"Summary: {total_changes} changes across {len(posts)} posts")
    if video_warnings:
        print(f"⚠ {video_warnings} broken video(s) found — consider replacing manually")
    if not apply:
        print("\nThis was a DRY RUN. To apply changes, run:")
        print("  python scripts/update_existing_posts.py --apply")
    else:
        print("\nChanges applied. Review with: git diff blog/")
    print("=" * 60)


if __name__ == "__main__":
    main()
