#!/usr/bin/env python3
"""
Comprehensive Blog Post Fixer for SteadiDay

Fixes:
1. Canonical URLs (must use custom domain)
2. Open Graph URLs (og:url)
3. Twitter URLs (twitter:url)
4. Schema.org URLs
5. Title length (warns if over 60 characters)

Usage:
    python fix_blog_posts.py [blog_directory]
    
Example:
    python fix_blog_posts.py ./blog
"""

import os
import re
import sys
from pathlib import Path

# The correct base URL (your custom domain)
CORRECT_DOMAIN = "https://www.steadiday.com"

# Wrong patterns to find and replace
WRONG_DOMAINS = [
    r'https://scm-solutions-llc\.github\.io/steadiday',
    r'https://scm-solutions-llc\.github\.io',
    r'http://scm-solutions-llc\.github\.io/steadiday',
    r'http://scm-solutions-llc\.github\.io',
]


def check_title_length(content: str, filepath: Path) -> list:
    """Check if title is under 60 characters."""
    warnings = []
    
    # Check <title> tag
    title_match = re.search(r'<title>([^<]+)</title>', content)
    if title_match:
        title = title_match.group(1)
        # Remove " - SteadiDay Blog" or similar suffix for counting
        clean_title = re.sub(r'\s*[-|]\s*SteadiDay.*$', '', title)
        if len(clean_title) > 60:
            warnings.append(f"  ⚠️  Title too long ({len(clean_title)} chars): \"{clean_title[:50]}...\"")
    
    # Check og:title
    og_title_match = re.search(r'<meta property="og:title" content="([^"]+)"', content)
    if og_title_match:
        og_title = og_title_match.group(1)
        if len(og_title) > 60:
            warnings.append(f"  ⚠️  og:title too long ({len(og_title)} chars)")
    
    return warnings


def fix_urls_in_file(filepath: Path) -> tuple[bool, list[str], list[str]]:
    """
    Fix all URLs in a single HTML file.
    
    Returns:
        tuple: (was_modified, list_of_changes, list_of_warnings)
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    changes = []
    warnings = []
    
    # Check title length
    title_warnings = check_title_length(content, filepath)
    warnings.extend(title_warnings)
    
    # Fix all wrong domain references
    for pattern in WRONG_DOMAINS:
        matches = re.findall(pattern, content)
        if matches:
            for match in set(matches):
                changes.append(f"  Fixed URL: {match} → {CORRECT_DOMAIN}")
            content = re.sub(pattern, CORRECT_DOMAIN, content)
    
    # Specifically check and fix key meta tags
    meta_tags_to_check = [
        ('canonical', r'<link rel="canonical" href="([^"]+)"'),
        ('og:url', r'<meta property="og:url" content="([^"]+)"'),
        ('twitter:url', r'<meta name="twitter:url" content="([^"]+)"'),
        ('og:image', r'<meta property="og:image" content="([^"]+)"'),
        ('twitter:image', r'<meta name="twitter:image" content="([^"]+)"'),
    ]
    
    for tag_name, pattern in meta_tags_to_check:
        match = re.search(pattern, content)
        if match:
            url = match.group(1)
            if 'github.io' in url:
                warnings.append(f"  ⚠️  {tag_name} still contains github.io after fix attempt")
    
    # Check if file was modified
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, changes, warnings
    
    return False, changes, warnings


def scan_and_fix_blog_directory(blog_dir: str) -> dict:
    """
    Scan all HTML files in the blog directory and fix URLs.
    """
    blog_path = Path(blog_dir)
    
    if not blog_path.exists():
        print(f"❌ Error: Directory '{blog_dir}' does not exist")
        sys.exit(1)
    
    stats = {
        "total_files": 0,
        "files_modified": 0,
        "files_with_warnings": 0,
        "files_already_correct": 0,
        "all_warnings": [],
    }
    
    html_files = list(blog_path.glob("**/*.html"))
    stats["total_files"] = len(html_files)
    
    print(f"📂 Scanning {len(html_files)} HTML files in '{blog_dir}'...")
    print(f"🔗 Correct domain: {CORRECT_DOMAIN}")
    print("-" * 70)
    
    for filepath in html_files:
        modified, changes, warnings = fix_urls_in_file(filepath)
        
        if modified or warnings:
            print(f"\n📄 {filepath.name}")
            
            if modified:
                stats["files_modified"] += 1
                print("  ✅ URLs fixed:")
                for change in changes:
                    print(change)
            
            if warnings:
                stats["files_with_warnings"] += 1
                stats["all_warnings"].append((filepath.name, warnings))
                for warning in warnings:
                    print(warning)
        else:
            stats["files_already_correct"] += 1
    
    return stats


def main():
    blog_dir = sys.argv[1] if len(sys.argv) > 1 else "blog"
    
    print("=" * 70)
    print("🔧 SteadiDay Blog Post Fixer")
    print("   Fixes: canonical, og:url, twitter:url, schema.org URLs")
    print("   Checks: title length (should be < 60 chars)")
    print("=" * 70)
    print()
    
    stats = scan_and_fix_blog_directory(blog_dir)
    
    print()
    print("=" * 70)
    print("📊 Summary")
    print("=" * 70)
    print(f"Total HTML files scanned:    {stats['total_files']}")
    print(f"Files with URLs fixed:       {stats['files_modified']}")
    print(f"Files with warnings:         {stats['files_with_warnings']}")
    print(f"Files already correct:       {stats['files_already_correct']}")
    
    if stats["all_warnings"]:
        print()
        print("⚠️  Files needing manual attention:")
        print("-" * 70)
        for filename, warnings in stats["all_warnings"]:
            print(f"\n{filename}:")
            for w in warnings:
                print(w)
    
    if stats["files_modified"]:
        print()
        print("=" * 70)
        print("📝 Next Steps")
        print("=" * 70)
        print("1. Review the changes above")
        print("2. For any title warnings, manually shorten the titles")
        print("3. Commit and push:")
        print()
        print("   git add .")
        print("   git commit -m 'Fix blog post URLs and SEO issues'")
        print("   git push")
        print()
        print("4. Request re-indexing in Bing Webmaster Tools")
    else:
        print()
        print("✨ All URLs are correct!")
        
        if stats["all_warnings"]:
            print("⚠️  But please review the warnings above.")


if __name__ == "__main__":
    main()
