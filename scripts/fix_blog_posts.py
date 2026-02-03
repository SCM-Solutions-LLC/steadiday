#!/usr/bin/env python3
"""
Comprehensive Blog Post Fixer for SteadiDay
"""

import os
import re
import sys
from pathlib import Path

CORRECT_DOMAIN = "https://www.steadiday.com"

WRONG_DOMAINS = [
    r'https://scm-solutions-llc\.github\.io/steadiday',
    r'https://scm-solutions-llc\.github\.io',
    r'http://scm-solutions-llc\.github\.io/steadiday',
    r'http://scm-solutions-llc\.github\.io',
]


def check_title_length(content: str, filepath: Path) -> list:
    warnings = []
    title_match = re.search(r'<title>([^<]+)</title>', content)
    if title_match:
        title = title_match.group(1)
        clean_title = re.sub(r'\s*[-|]\s*SteadiDay.*$', '', title)
        if len(clean_title) > 60:
            warnings.append(f"  ⚠️  Title too long ({len(clean_title)} chars): \"{clean_title[:50]}...\"")
    return warnings


def fix_urls_in_file(filepath: Path) -> tuple:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    changes = []
    warnings = []
    
    title_warnings = check_title_length(content, filepath)
    warnings.extend(title_warnings)
    
    for pattern in WRONG_DOMAINS:
        matches = re.findall(pattern, content)
        if matches:
            for match in set(matches):
                changes.append(f"  Fixed URL: {match} → {CORRECT_DOMAIN}")
            content = re.sub(pattern, CORRECT_DOMAIN, content)
    
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, changes, warnings
    
    return False, changes, warnings


def main():
    blog_dir = sys.argv[1] if len(sys.argv) > 1 else "blog"
    blog_path = Path(blog_dir)
    
    if not blog_path.exists():
        print(f"❌ Error: Directory '{blog_dir}' does not exist")
        sys.exit(0)  # Exit with 0 so the action doesn't fail
    
    html_files = list(blog_path.glob("**/*.html"))
    
    print(f"📂 Scanning {len(html_files)} HTML files in '{blog_dir}'...")
    print(f"🔗 Correct domain: {CORRECT_DOMAIN}")
    print("-" * 70)
    
    files_modified = 0
    
    for filepath in html_files:
        modified, changes, warnings = fix_urls_in_file(filepath)
        
        if modified or warnings:
            print(f"\n📄 {filepath.name}")
            
            if modified:
                files_modified += 1
                print("  ✅ URLs fixed:")
                for change in changes:
                    print(change)
            
            for warning in warnings:
                print(warning)
    
    print(f"\n✅ Done! Fixed {files_modified} files.")


if __name__ == "__main__":
    main()
