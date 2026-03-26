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

# 1. youtube-nocookie.com → youtube.com (nocookie is blocked by many browsers/extensions)

# 2. Removes frameborder=“0” (deprecated HTML5 attribute, already handled by CSS)

# 3. Removes loading=“lazy” from video iframes (causes iframes to never load in height:0 containers)

# 4. Updates referrerpolicy to strict-origin-when-cross-origin (matches YouTube’s recommended embed)

set -e

BLOG_DIR=“blog”

if [ ! -d “$BLOG_DIR” ]; then
echo “Error: ‘$BLOG_DIR’ directory not found.”
echo “Make sure you run this script from your repo root.”
exit 1
fi

# Count how many files have the old embed

COUNT=$(grep -rl “youtube-nocookie.com” “$BLOG_DIR”/*.html 2>/dev/null | wc -l)

if [ “$COUNT” -eq 0 ]; then
echo “No files with youtube-nocookie.com found. Nothing to fix.”
exit 0
fi

echo “Found $COUNT blog file(s) with broken YouTube embeds.”
echo “Fixing…”

# Apply all fixes

find “$BLOG_DIR” -name “*.html” -exec sed -i’’   
-e ‘s|youtube-nocookie.com|youtube.com|g’   
-e ‘s| frameborder=“0”||g’   
-e ‘s| loading=“lazy” referrerpolicy=“no-referrer-when-downgrade”| referrerpolicy=“strict-origin-when-cross-origin”|g’   
{} +

echo “Done! Fixed $COUNT file(s).”
echo “”
echo “Now commit and push:”
echo “  git add blog/”
echo “  git commit -m "Fix broken YouTube embeds in existing blog posts"”
echo “  git push”