#!/usr/bin/env python3
"""
SteadiDay Blog Generator
Generates SEO-optimized blog posts for health and wellness topics.
"""

import os
import sys
import json
import random
import re
from datetime import datetime
import anthropic

# App links - update these as needed
APP_LINKS = {
    "website": "https://www.steadiday.com",
    "base_url": "https://scm-solutions-llc.github.io/steadiday",
}

# SEO-optimized topics with target keywords
# Using inclusive language: "older adults" and "seniors" instead of "50+"
TOPIC_CATEGORIES = [
    # Medication Management
    {"topic": "how to remember to take medication", "keyword": "how to remember to take medication"},
    {"topic": "pill reminder app for seniors", "keyword": "pill reminder app for seniors"},
    {"topic": "medication management tips for older adults", "keyword": "medication management older adults"},
    {"topic": "organizing daily medications safely", "keyword": "organizing medications safely"},
    {"topic": "what to do if you miss a medication dose", "keyword": "missed medication dose"},
    
    # Health Tracking
    {"topic": "best health apps for seniors", "keyword": "health apps for seniors"},
    {"topic": "tracking health metrics at home", "keyword": "tracking health metrics"},
    {"topic": "understanding your blood pressure readings", "keyword": "understanding blood pressure readings"},
    {"topic": "simple ways to monitor your heart health", "keyword": "monitor heart health"},
    {"topic": "health metrics to track as you age", "keyword": "health metrics to track"},
    
    # Daily Wellness
    {"topic": "morning routine for healthy aging", "keyword": "morning routine healthy aging"},
    {"topic": "staying hydrated tips for older adults", "keyword": "staying hydrated older adults"},
    {"topic": "simple exercises for older adults at home", "keyword": "exercises for older adults"},
    {"topic": "sleep tips for better rest", "keyword": "sleep tips for seniors"},
    {"topic": "how to stay healthy as you age", "keyword": "how to stay healthy aging"},
    
    # Mental Wellness
    {"topic": "mindfulness for seniors beginners guide", "keyword": "mindfulness for seniors"},
    {"topic": "reducing stress in daily life", "keyword": "reducing stress daily life"},
    {"topic": "staying mentally sharp with daily habits", "keyword": "staying mentally sharp"},
    {"topic": "brain exercises for cognitive health", "keyword": "brain exercises cognitive health"},
    {"topic": "managing anxiety with simple techniques", "keyword": "managing anxiety techniques"},
    
    # Independence & Safety
    {"topic": "apps to help older adults stay independent", "keyword": "apps older adults independent"},
    {"topic": "home safety tips for aging in place", "keyword": "home safety aging in place"},
    {"topic": "emergency preparedness for seniors", "keyword": "emergency preparedness seniors"},
    {"topic": "fall prevention strategies at home", "keyword": "fall prevention strategies"},
    
    # Caregiving & Family
    {"topic": "helping aging parents manage health", "keyword": "help aging parents health"},
    {"topic": "how to prepare for a doctor appointment", "keyword": "prepare for doctor appointment"},
    {"topic": "communicating health needs with family", "keyword": "communicating health needs family"},
]

# SteadiDay features categorized by free/premium
STEADIDAY_FEATURES = {
    "free": [
        "medication reminders",
        "daily task management",
        "simple health tracking",
        "mindful break exercises",
    ],
    "premium": [
        "advanced health insights and trends",
        "Apple Health integration for comprehensive tracking",
        "unlimited medication tracking",
        "personalized wellness recommendations",
        "detailed progress reports",
    ]
}


def generate_blog_post(topic_override: str = None) -> dict:
    """Generate an SEO-optimized blog post using Claude API."""
    
    client = anthropic.Anthropic()
    
    # Select topic
    if topic_override and topic_override.strip():
        selected = {"topic": topic_override, "keyword": topic_override.lower()}
    else:
        selected = random.choice(TOPIC_CATEGORIES)
    
    topic = selected["topic"]
    keyword = selected["keyword"]
    
    # Select features to mention
    free_feature = random.choice(STEADIDAY_FEATURES["free"])
    premium_feature = random.choice(STEADIDAY_FEATURES["premium"])
    
    prompt = f"""You are a health and wellness content writer for SteadiDay, a mobile app designed to help older adults live healthier, more organized lives.

Write a blog post about: "{topic}"
Target SEO keyword: "{keyword}"

TARGET AUDIENCE:
- Older adults interested in maintaining their health and independence
- People who may be managing medications or health conditions  
- Caregivers helping aging parents or loved ones
- Anyone who appreciates practical, actionable health advice

IMPORTANT LANGUAGE GUIDELINES:
- Use "older adults" or "seniors" instead of "adults 50+" or "people over 50"
- Keep the tone warm, encouraging, and respectful - never condescending
- Write in a conversational, first-person style ("I've found that..." or "You might notice...")
- Avoid making readers feel old - focus on capability and independence

BLOG REQUIREMENTS:

1. TITLE: Create an engaging, SEO-friendly title that includes the keyword "{keyword}" naturally

2. LENGTH: 900-1300 words of valuable content

3. STRUCTURE:
   - Opening paragraph that connects with the reader and includes the keyword naturally
   - 4-6 sections with clear H2 subheadings (use one subheading that includes the keyword)
   - Practical, actionable advice throughout
   - Conversational transitions between sections (no bullet points or numbered lists in the main content)

4. STEADIDAY MENTIONS (keep natural, not salesy):
   - Mid-article: Briefly mention how SteadiDay's {free_feature} can help (1-2 sentences max)
   - Later: For readers wanting more, mention the premium {premium_feature} feature
   - End: Close with a CTA directing to steadiday.com

5. CREDIBILITY:
   - Include 2-3 links to credible sources (Mayo Clinic, CDC, NIH, Harvard Health, etc.)
   - Use real, working URLs from these trusted health organizations
   - Weave statistics or research findings naturally into the content

6. SEO ELEMENTS:
   - Meta description: 150-160 characters including the keyword
   - Include the keyword in: title, first paragraph, one H2 heading, and conclusion
   - Natural keyword density (don't force it)

FORMAT YOUR RESPONSE AS JSON:
{{
    "title": "Your SEO-Optimized Title Here",
    "meta_description": "150-160 character description with keyword",
    "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
    "content": "Full HTML content with <h2> tags for headings and <p> tags for paragraphs. Include <a href='url' target='_blank' rel='noopener'>anchor text</a> for source links."
}}

CRITICAL: 
- Return ONLY valid JSON, no markdown code blocks
- The content should be HTML formatted (h2, p, a tags)
- Do NOT use bullet points or numbered lists
- Do NOT end with community engagement prompts (no "share your tips" requests)
- End the article after the SteadiDay CTA"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=3000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    response_text = message.content[0].text
    
    # Clean up response if needed
    response_text = response_text.strip()
    if response_text.startswith("```json"):
        response_text = response_text[7:]
    if response_text.startswith("```"):
        response_text = response_text[3:]
    if response_text.endswith("```"):
        response_text = response_text[:-3]
    response_text = response_text.strip()
    
    # Parse JSON response
    try:
        blog_data = json.loads(response_text)
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        print(f"Response was: {response_text[:500]}...")
        raise
    
    # Create slug from title
    title = blog_data.get("title", topic)
    slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')[:50]
    
    return {
        "title": title,
        "meta_description": blog_data.get("meta_description", ""),
        "tags": blog_data.get("tags", []),
        "content": blog_data.get("content", ""),
        "slug": slug,
        "date": datetime.now().strftime('%Y-%m-%d'),
        "keyword": keyword,
    }


def create_html_file(post_data: dict) -> str:
    """Generate the full HTML blog post file."""
    
    date_formatted = datetime.strptime(post_data['date'], '%Y-%m-%d').strftime('%B %d, %Y')
    word_count = len(post_data['content'].split())
    read_time = max(1, round(word_count / 200))
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{post_data['title']} - SteadiDay Blog</title>
    <meta name="description" content="{post_data['meta_description']}">
    <meta name="keywords" content="{', '.join(post_data['tags'])}">
    
    <meta property="og:title" content="{post_data['title']}">
    <meta property="og:description" content="{post_data['meta_description']}">
    <meta property="og:type" content="article">
    <meta property="og:url" content="{APP_LINKS['base_url']}/blog/{post_data['date']}-{post_data['slug']}.html">
    
    <link rel="canonical" href="{APP_LINKS['base_url']}/blog/{post_data['date']}-{post_data['slug']}.html">
    
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.7;
            color: #333;
            background-color: #f8f9fa;
        }}
        
        .nav {{
            background: white;
            padding: 15px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        
        .nav-container {{
            max-width: 800px;
            margin: 0 auto;
            padding: 0 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .nav a {{
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
        }}
        
        .nav a:hover {{ text-decoration: underline; }}
        
        .article-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 60px 20px;
            text-align: center;
        }}
        
        .article-header h1 {{
            max-width: 800px;
            margin: 0 auto 15px;
            font-size: 2.2rem;
            line-height: 1.3;
        }}
        
        .article-meta {{
            font-size: 1rem;
            opacity: 0.9;
        }}
        
        .article-container {{
            max-width: 700px;
            margin: 0 auto;
            padding: 40px 20px;
            background: white;
            margin-top: -30px;
            border-radius: 12px 12px 0 0;
            position: relative;
        }}
        
        .article-content h2 {{
            font-size: 1.5rem;
            margin: 35px 0 15px;
            color: #333;
        }}
        
        .article-content p {{
            margin-bottom: 20px;
            font-size: 1.1rem;
            color: #444;
        }}
        
        .article-content a {{ color: #667eea; }}
        .article-content a:hover {{ text-decoration: none; }}
        
        .cta-box {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 12px;
            text-align: center;
            margin: 40px 0;
        }}
        
        .cta-box h3 {{
            margin-bottom: 10px;
            font-size: 1.3rem;
        }}
        
        .cta-box p {{
            color: white !important;
            margin-bottom: 15px;
        }}
        
        .cta-button {{
            display: inline-block;
            background: white;
            color: #667eea;
            padding: 12px 30px;
            border-radius: 25px;
            text-decoration: none;
            font-weight: 600;
        }}
        
        .cta-button:hover {{ opacity: 0.9; }}
        
        .back-to-blog {{
            max-width: 700px;
            margin: 0 auto;
            padding: 20px;
            text-align: center;
            background: white;
        }}
        
        .back-to-blog a {{
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
        }}
        
        .footer {{
            text-align: center;
            padding: 30px;
            color: #666;
            font-size: 0.9rem;
            background: white;
        }}
        
        .footer a {{ color: #667eea; }}
    </style>
</head>
<body>
    <nav class="nav">
        <div class="nav-container">
            <a href="index.html">← Back to Blog</a>
            <a href="{APP_LINKS['website']}">Download SteadiDay</a>
        </div>
    </nav>
    
    <header class="article-header">
        <h1>{post_data['title']}</h1>
        <div class="article-meta">{date_formatted} • By SteadiDay Team • {read_time} min read</div>
    </header>
    
    <article class="article-container">
        <div class="article-content">
            {post_data['content']}
            
            <div class="cta-box">
                <h3>Ready to Take Control of Your Health?</h3>
                <p>SteadiDay helps you manage medications, track your wellness, and build healthy habits—all designed for older adults.</p>
                <a href="{APP_LINKS['website']}" class="cta-button">Download SteadiDay Free</a>
            </div>
        </div>
    </article>
    
    <div class="back-to-blog">
        <a href="index.html">← See all blog posts</a>
    </div>
    
    <footer class="footer">
        <p>&copy; {datetime.now().year} SteadiDay. All rights reserved. | <a href="../index.html">Home</a> | <a href="../liability.html">Terms</a></p>
    </footer>
</body>
</html>"""
    
    return html


def update_blog_index(post_data: dict):
    """Update the blog index.html with the new post."""
    
    index_path = "blog/index.html"
    
    if not os.path.exists(index_path):
        print(f"Warning: {index_path} not found, skipping index update")
        return
    
    with open(index_path, 'r', encoding='utf-8') as f:
        index_content = f.read()
    
    date_formatted = datetime.strptime(post_data['date'], '%Y-%m-%d').strftime('%B %d, %Y')
    word_count = len(post_data['content'].split())
    read_time = max(1, round(word_count / 200))
    
    # Create excerpt from content (first ~200 chars of text)
    excerpt = re.sub(r'<[^>]+>', '', post_data['content'])[:250]
    excerpt = excerpt.rsplit(' ', 1)[0] + '...'
    
    filename = f"{post_data['date']}-{post_data['slug']}.html"
    
    new_entry = f"""<article class="blog-card">
                <h2><a href="{filename}">{post_data['title']}</a></h2>
                <div class="blog-meta">{date_formatted} • {read_time} min read</div>
                <p class="blog-excerpt">{excerpt}</p>
                <a href="{filename}" class="read-more">Read more →</a>
            </article>
            
            """
    
    # Insert after the marker
    marker = "<!--BLOG_ENTRIES_START-->"
    if marker in index_content:
        index_content = index_content.replace(
            marker,
            marker + "\n            " + new_entry
        )
        
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(index_content)
        print(f"✅ Updated {index_path}")
    else:
        print(f"Warning: Marker not found in {index_path}")


def set_github_env(key: str, value: str):
    """Set environment variable for GitHub Actions."""
    env_file = os.environ.get('GITHUB_ENV')
    if env_file:
        with open(env_file, 'a') as f:
            # Handle multi-line values
            if '\n' in value:
                import uuid
                delimiter = uuid.uuid4().hex
                f.write(f"{key}<<{delimiter}\n{value}\n{delimiter}\n")
            else:
                f.write(f"{key}={value}\n")
    else:
        print(f"  [ENV] {key}={value[:50]}...")


def main():
    topic_override = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].strip() else None
    
    print("🚀 Starting SteadiDay Blog Generator...")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}")
    
    if topic_override:
        print(f"📝 Using custom topic: {topic_override}")
    else:
        print("🎲 Selecting random SEO topic...")
    
    # Generate the blog post
    print("✨ Generating blog content with Claude...")
    post_data = generate_blog_post(topic_override)
    
    print(f"📰 Title: {post_data['title']}")
    print(f"🔑 Target keyword: {post_data['keyword']}")
    
    # Create blog directory if needed
    os.makedirs("blog", exist_ok=True)
    
    # Generate HTML
    html_content = create_html_file(post_data)
    
    # Save the file
    filename = f"{post_data['date']}-{post_data['slug']}.html"
    filepath = f"blog/{filename}"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"💾 Saved to: {filepath}")
    
    # Update blog index
    update_blog_index(post_data)
    
    # Set GitHub Actions environment variables
    set_github_env("BLOG_TITLE", post_data['title'])
    set_github_env("BLOG_SLUG", post_data['slug'])
    set_github_env("BLOG_DATE", post_data['date'])
    
    print("✅ Blog draft generated successfully!")


if __name__ == "__main__":
    main()
