#!/usr/bin/env bash

# fix-youtube-embeds.sh

# One-time script to fix broken YouTube embeds in all existing blog posts.

# Run from your repo root (the directory that contains the blog/ folder).

# 

# Usage:

# cd /path/to/your/steadiday-repo

# bash fix-youtube-embeds.sh

# 

# What it fixes:

# 1. youtube-nocookie.com -> youtube.com (nocookie is blocked by many browsers/extensions)

# 2. Removes frameborder=“0” (deprecated HTML5 attribute, already handled by CSS)

# 3. Removes loading=“lazy” from video iframes (causes iframes to never load in height:0 containers)

# 4. Updates referrerpolicy to strict-origin-when-cross-origin (YouTube’s recommended embed)

# 5. Checks each embedded video ID against YouTube’s oEmbed API and removes dead videos

set -e

BLOG_DIR=“blog”

if [ ! -d “$BLOG_DIR” ]; then
echo “Error: ‘$BLOG_DIR’ directory not found.”
echo “Make sure you run this script from your repo root.”
exit 1
fi

echo “=== SteadiDay Blog YouTube Embed Fixer ===”
echo “”

# — Step 1: Fix embed attributes —

COUNT=$(grep -rl “youtube-nocookie|frameborder” “$BLOG_DIR”/*.html 2>/dev/null | wc -l || echo 0)

if [ “$COUNT” -gt 0 ]; then
echo “Step 1: Fixing embed attributes in $COUNT file(s)…”
find “$BLOG_DIR” -name “*.html” -exec sed -i’’   
-e ‘s|youtube-nocookie.com|youtube.com|g’   
-e ‘s| frameborder=“0”||g’   
-e ‘s| loading=“lazy” referrerpolicy=“no-referrer-when-downgrade”| referrerpolicy=“strict-origin-when-cross-origin”|g’   
{} +
echo “  Done.”
else
echo “Step 1: No attribute fixes needed.”
fi

# — Step 2: Check each embedded video ID and remove dead ones —

echo “”
echo “Step 2: Verifying embedded video IDs against YouTube…”

FIXED_VIDEOS=0

for file in “$BLOG_DIR”/*.html; do
[ -f “$file” ] || continue

```
# Extract video IDs from youtube.com/embed/XXXXX patterns
VIDEO_IDS=$(grep -oE 'youtube\.com/embed/[A-Za-z0-9_-]{10,12}' "$file" 2>/dev/null | sed 's|youtube\.com/embed/||' || true)

for vid in $VIDEO_IDS; do
    [ -z "$vid" ] && continue

    # Check if video is available via YouTube oEmbed API
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
        "https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=${vid}&format=json" \
        2>/dev/null || echo "000")

    if [ "$HTTP_CODE" != "200" ]; then
        echo "  DEAD: $vid in $(basename "$file") (HTTP $HTTP_CODE) -- removing embed"

        # Use python to safely remove the video container and caption
        python3 -c "
```

import re
with open(’$file’, ‘r’) as f:
content = f.read()

# Remove video container div with this specific ID and its caption

content = re.sub(
r’<div class="video-container"><iframe[^>]*embed/$vid[^>]*></iframe></div>\s*<p class="video-caption">.*?</p>’,
‘’,
content,
flags=re.DOTALL
)
with open(’$file’, ‘w’) as f:
f.write(content)
“ 2>/dev/null && FIXED_VIDEOS=$((FIXED_VIDEOS + 1))
else
echo “  OK:   $vid in $(basename “$file”)”
fi

```
    # Small delay to avoid hammering YouTube's API
    sleep 0.5
done
```

done

echo “”
echo “=== Summary ===”
echo “  Attribute fixes: $COUNT file(s)”
echo “  Dead videos removed: $FIXED_VIDEOS”
echo “”

if [ “$COUNT” -gt 0 ] || [ “$FIXED_VIDEOS” -gt 0 ]; then
echo “Now commit and push:”
echo “  git add blog/”
echo “  git commit -m "Fix broken YouTube embeds in existing blog posts"”
echo “  git push”
else
echo “Nothing to fix. All embeds look good.”
fi