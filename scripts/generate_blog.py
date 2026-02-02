#!/usr/bin/env python3
"""
SteadiDay Blog Generator
Generates SEO-optimized blog posts with stock photos matching SteadiDay's brand colors.
"""

import os
import sys
import json
import random
import re
from datetime import datetime
import anthropic

# App links
APP_LINKS = {
    "website": "https://www.steadiday.com",
    "base_url": "https://scm-solutions-llc.github.io/steadiday",
}

# Curated Unsplash photos for each category (free to use)
STOCK_PHOTOS = {
    "medication": [
        "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=800&q=80",
        "https://images.unsplash.com/photo-1471864190281-a93a3070b6de?w=800&q=80",
        "https://images.unsplash.com/photo-1587854692152-cbe660dbde88?w=800&q=80",
        "https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=800&q=80",
    ],
    "health_tracking": [
        "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=800&q=80",
        "https://images.unsplash.com/photo-1559757175-5700dde675bc?w=800&q=80",
        "https://images.unsplash.com/photo-1505751172876-fa1923c5c528?w=800&q=80",
        "https://images.unsplash.com/photo-1579684385127-1ef15d508118?w=800&q=80",
    ],
    "heart_health": [
        "https://images.unsplash.com/photo-1505576399279-565b52d4ac71?w=800&q=80",
        "https://images.unsplash.com/photo-1511688878353-3a2f5be94cd7?w=800&q=80",
        "https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=800&q=80",
        "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=800&q=80",
    ],
    "mental_wellness": [
        "https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=800&q=80",
        "https://images.unsplash.com/photo-1499209974431-9dddcece7f88?w=800&q=80",
        "https://images.unsplash.com/photo-1518611012118-696072aa579a?w=800&q=80",
        "https://images.unsplash.com/photo-1507120410856-1f35574c3b45?w=800&q=80",
        "https://images.unsplash.com/photo-1528715471579-d1bcf0ba5e83?w=800&q=80",
    ],
    "brain_health": [
        "https://images.unsplash.com/photo-1559757175-0eb30cd8c063?w=800&q=80",
        "https://images.unsplash.com/photo-1456406644174-8ddd4cd52a06?w=800&q=80",
        "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=800&q=80",
        "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=800&q=80",
    ],
    "daily_wellness": [
        "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=800&q=80",
        "https://images.unsplash.com/photo-1498837167922-ddd27525d352?w=800&q=80",
        "https://images.unsplash.com/photo-1541534741688-6078c6bfb5c5?w=800&q=80",
        "https://images.unsplash.com/photo-1476480862126-209bfaa8edc8?w=800&q=80",
        "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=800&q=80",
    ],
    "sleep": [
        "https://images.unsplash.com/photo-1531353826977-0941b4779a1c?w=800&q=80",
        "https://images.unsplash.com/photo-1515894203077-9cd36032142f?w=800&q=80",
        "https://images.unsplash.com/photo-1507652313519-d4e9174996dd?w=800&q=80",
    ],
    "safety": [
        "https://images.unsplash.com/photo-1582719508461-905c673771fd?w=800&q=80",
        "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80",
        "https://images.unsplash.com/photo-1484154218962-a197022b5858?w=800&q=80",
    ],
    "family": [
        "https://images.unsplash.com/photo-1511895426328-dc8714191300?w=800&q=80",
        "https://images.unsplash.com/photo-1516733968668-dbdce39c0651?w=800&q=80",
        "https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=800&q=80",
    ],
    "healthcare": [
        "https://images.unsplash.com/photo-1551076805-e1869033e561?w=800&q=80",
        "https://images.unsplash.com/photo-1579684385127-1ef15d508118?w=800&q=80",
        "https://images.unsplash.com/photo-1505751172876-fa1923c5c528?w=800&q=80",
    ],
    "fitness": [
        "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=800&q=80",
        "https://images.unsplash.com/photo-1518611012118-696072aa579a?w=800&q=80",
        "https://images.unsplash.com/photo-1538805060514-97d9cc17730c?w=800&q=80",
        "https://images.unsplash.com/photo-1552674605-db6ffd4facb5?w=800&q=80",
    ],
    "nutrition": [
        "https://images.unsplash.com/photo-1490645935967-10de6ba17061?w=800&q=80",
        "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=800&q=80",
        "https://images.unsplash.com/photo-1498837167922-ddd27525d352?w=800&q=80",
        "https://images.unsplash.com/photo-1494390248081-4e521a5940db?w=800&q=80",
    ],
    "hydration": [
        "https://images.unsplash.com/photo-1548839140-29a749e1cf4d?w=800&q=80",
        "https://images.unsplash.com/photo-1523362628745-0c100150b504?w=800&q=80",
    ],
    "tech": [
        "https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=800&q=80",
        "https://images.unsplash.com/photo-1434494878577-86c23bcb06b9?w=800&q=80",
        "https://images.unsplash.com/photo-1551650975-87deedd944c3?w=800&q=80",
    ],
}

# Topic categories with SEO keywords and photo categories
TOPIC_CATEGORIES = [
    # Medication Management
    {"topic": "how to remember to take medication", "keyword": "how to remember to take medication", "tag": "Medication Tips", "photo_category": "medication"},
    {"topic": "pill reminder app for seniors", "keyword": "pill reminder app for seniors", "tag": "Medication Tips", "photo_category": "medication"},
    {"topic": "medication management tips for older adults", "keyword": "medication management older adults", "tag": "Medication Tips", "photo_category": "medication"},
    {"topic": "organizing daily medications safely", "keyword": "organizing medications safely", "tag": "Medication Tips", "photo_category": "medication"},
    {"topic": "what to do if you miss a medication dose", "keyword": "missed medication dose", "tag": "Medication Tips", "photo_category": "medication"},
    
    # Health Tracking
    {"topic": "best health apps for seniors", "keyword": "health apps for seniors", "tag": "Health Tech", "photo_category": "tech"},
    {"topic": "tracking health metrics at home", "keyword": "tracking health metrics", "tag": "Health Tracking", "photo_category": "health_tracking"},
    {"topic": "understanding your blood pressure readings", "keyword": "understanding blood pressure readings", "tag": "Heart Health", "photo_category": "heart_health"},
    {"topic": "simple ways to monitor your heart health", "keyword": "monitor heart health", "tag": "Heart Health", "photo_category": "heart_health"},
    {"topic": "health metrics to track as you age", "keyword": "health metrics to track", "tag": "Health Tracking", "photo_category": "health_tracking"},
    
    # Daily Wellness
    {"topic": "morning routine for healthy aging", "keyword": "morning routine healthy aging", "tag": "Daily Wellness", "photo_category": "daily_wellness"},
    {"topic": "staying hydrated tips for older adults", "keyword": "staying hydrated older adults", "tag": "Daily Wellness", "photo_category": "hydration"},
    {"topic": "simple exercises for older adults at home", "keyword": "exercises for older adults", "tag": "Fitness", "photo_category": "fitness"},
    {"topic": "sleep tips for better rest", "keyword": "sleep tips for seniors", "tag": "Sleep Health", "photo_category": "sleep"},
    {"topic": "how to stay healthy as you age", "keyword": "how to stay healthy aging", "tag": "Daily Wellness", "photo_category": "daily_wellness"},
    {"topic": "nutrition tips for healthy aging", "keyword": "nutrition healthy aging", "tag": "Nutrition", "photo_category": "nutrition"},
    
    # Mental Wellness
    {"topic": "mindfulness for seniors beginners guide", "keyword": "mindfulness for seniors", "tag": "Mental Wellness", "photo_category": "mental_wellness"},
    {"topic": "reducing stress in daily life", "keyword": "reducing stress daily life", "tag": "Mental Wellness", "photo_category": "mental_wellness"},
    {"topic": "staying mentally sharp with daily habits", "keyword": "staying mentally sharp", "tag": "Brain Health", "photo_category": "brain_health"},
    {"topic": "brain exercises for cognitive health", "keyword": "brain exercises cognitive health", "tag": "Brain Health", "photo_category": "brain_health"},
    {"topic": "managing anxiety with simple techniques", "keyword": "managing anxiety techniques", "tag": "Mental Wellness", "photo_category": "mental_wellness"},
    
    # Independence & Safety
    {"topic": "apps to help older adults stay independent", "keyword": "apps older adults independent", "tag": "Independence", "photo_category": "tech"},
    {"topic": "home safety tips for aging in place", "keyword": "home safety aging in place", "tag": "Safety", "photo_category": "safety"},
    {"topic": "emergency preparedness for seniors", "keyword": "emergency preparedness seniors", "tag": "Safety", "photo_category": "safety"},
    {"topic": "fall prevention strategies at home", "keyword": "fall prevention strategies", "tag": "Safety", "photo_category": "safety"},
    
    # Caregiving & Family
    {"topic": "helping aging parents manage health", "keyword": "help aging parents health", "tag": "Family", "photo_category": "family"},
    {"topic": "how to prepare for a doctor appointment", "keyword": "prepare for doctor appointment", "tag": "Healthcare", "photo_category": "healthcare"},
    {"topic": "communicating health needs with family", "keyword": "communicating health needs family", "tag": "Family", "photo_category": "family"},
]

# SteadiDay features
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


def get_photo_url(category: str) -> str:
    """Get a random photo URL for the given category."""
    if category in STOCK_PHOTOS:
        return random.choice(STOCK_PHOTOS[category])
    return random.choice(STOCK_PHOTOS["daily_wellness"])


def generate_blog_post(topic_override: str = None) -> dict:
    """Generate an SEO-optimized blog post using Claude API."""
    
    client = anthropic.Anthropic()
    
    # Select topic
    if topic_override and topic_override.strip():
        selected = {
            "topic": topic_override, 
            "keyword": topic_override.lower(), 
            "tag": "Wellness",
            "photo_category": "daily_wellness"
        }
    else:
        selected = random.choice(TOPIC_CATEGORIES)
    
    topic = selected["topic"]
    keyword = selected["keyword"]
    tag = selected["tag"]
    photo_url = get_photo_url(selected["photo_category"])
    
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
- Do NOT end with community engagement prompts
- End the article after the SteadiDay CTA"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=3000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    response_text = message.content[0].text
    
    # Clean up response
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
        "tag": tag,
        "photo_url": photo_url,
    }


def create_html_file(post_data: dict) -> str:
    """Generate the full HTML blog post file with SteadiDay brand colors."""
    
    date_formatted = datetime.strptime(post_data['date'], '%Y-%m-%d').strftime('%B %d, %Y')
    word_count = len(post_data['content'].split())
    read_time = max(1, round(word_count / 200))
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-LF8H890XTV"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', 'G-LF8H890XTV');
    </script>
    
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{post_data['title']} - SteadiDay Blog</title>
    <meta name="description" content="{post_data['meta_description']}">
    <meta name="keywords" content="{', '.join(post_data['tags'])}">
    
    <meta property="og:title" content="{post_data['title']}">
    <meta property="og:description" content="{post_data['meta_description']}">
    <meta property="og:type" content="article">
    <meta property="og:image" content="{post_data['photo_url']}">
    <meta property="og:url" content="{APP_LINKS['base_url']}/blog/{post_data['date']}-{post_data['slug']}.html">
    
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{post_data['title']}">
    <meta name="twitter:description" content="{post_data['meta_description']}">
    <meta name="twitter:image" content="{post_data['photo_url']}">
    
    <link rel="canonical" href="{APP_LINKS['base_url']}/blog/{post_data['date']}-{post_data['slug']}.html">
    <link rel="icon" type="image/jpeg" href="../assets/icon.jpeg">
    
    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Merriweather:wght@400;700&family=Source+Sans+3:wght@400;500;600;700&display=swap" rel="stylesheet">
    
    <style>
        :root {{
            --cream: #FFFBF5;
            --cream-dark: #F7F3ED;
            --teal: #1A8A7D;
            --teal-dark: #147568;
            --teal-light: #E8F5F3;
            --navy: #1E3A5F;
            --navy-light: #2D4A6F;
            --charcoal: #2D3436;
            --charcoal-light: #5A6266;
            --white: #FFFFFF;
            --gold: #D4A853;
            --shadow-soft: 0 2px 12px rgba(30, 58, 95, 0.08);
            --shadow-medium: 0 4px 24px rgba(30, 58, 95, 0.12);
            --radius-md: 12px;
            --radius-lg: 20px;
        }}
        
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'Source Sans 3', -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 1.125rem;
            line-height: 1.8;
            color: var(--charcoal);
            background: var(--cream);
            -webkit-font-smoothing: antialiased;
        }}
        
        h1, h2, h3 {{
            font-family: 'Merriweather', Georgia, serif;
            font-weight: 700;
            line-height: 1.3;
            color: var(--navy);
        }}
        
        a {{
            color: var(--teal);
            text-decoration: none;
        }}
        
        a:hover {{
            color: var(--teal-dark);
        }}
        
        .nav {{
            background: var(--cream);
            padding: 1rem 0;
            border-bottom: 1px solid rgba(30, 58, 95, 0.08);
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        
        .nav-container {{
            max-width: 900px;
            margin: 0 auto;
            padding: 0 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .nav a {{
            color: var(--teal);
            font-weight: 600;
        }}
        
        .nav a:hover {{ 
            color: var(--teal-dark);
        }}
        
        .article-hero {{
            position: relative;
            height: 420px;
            background: linear-gradient(to bottom, rgba(30, 58, 95, 0.4), rgba(30, 58, 95, 0.7)), 
                        url('{post_data['photo_url']}') center/cover;
            display: flex;
            align-items: flex-end;
            padding: 3rem 2rem;
        }}
        
        .article-hero-content {{
            max-width: 800px;
            margin: 0 auto;
            width: 100%;
            color: var(--white);
        }}
        
        .article-tag {{
            display: inline-block;
            background: var(--teal);
            padding: 0.4rem 1rem;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            margin-bottom: 1rem;
        }}
        
        .article-hero h1 {{
            font-size: 2.5rem;
            line-height: 1.25;
            margin-bottom: 1rem;
            color: var(--white);
            text-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }}
        
        .article-meta {{
            font-size: 1rem;
            opacity: 0.9;
            display: flex;
            gap: 1.5rem;
            flex-wrap: wrap;
        }}
        
        .article-container {{
            max-width: 750px;
            margin: 0 auto;
            padding: 3rem 2rem;
            background: var(--white);
            margin-top: -3rem;
            border-radius: var(--radius-lg) var(--radius-lg) 0 0;
            position: relative;
            box-shadow: 0 -5px 30px rgba(30, 58, 95, 0.1);
        }}
        
        .article-content h2 {{
            font-size: 1.5rem;
            margin: 2.5rem 0 1rem;
            color: var(--navy);
            padding-top: 0.5rem;
        }}
        
        .article-content p {{
            margin-bottom: 1.5rem;
            font-size: 1.1rem;
            color: var(--charcoal);
            line-height: 1.85;
        }}
        
        .article-content a {{ 
            color: var(--teal); 
            text-decoration: underline;
            text-decoration-color: rgba(26, 138, 125, 0.3);
        }}
        
        .article-content a:hover {{ 
            text-decoration-color: var(--teal);
        }}
        
        .cta-box {{
            background: linear-gradient(135deg, var(--teal) 0%, var(--teal-dark) 100%);
            color: var(--white);
            padding: 2.5rem;
            border-radius: var(--radius-lg);
            text-align: center;
            margin: 3rem 0 2rem;
        }}
        
        .cta-box h3 {{
            margin-bottom: 0.75rem;
            font-size: 1.4rem;
            color: var(--white);
        }}
        
        .cta-box p {{
            color: rgba(255,255,255,0.95) !important;
            margin-bottom: 1.5rem;
            font-size: 1.05rem;
        }}
        
        .cta-button {{
            display: inline-block;
            background: var(--white);
            color: var(--teal);
            padding: 1rem 2.5rem;
            border-radius: var(--radius-md);
            text-decoration: none;
            font-weight: 700;
            font-size: 1.1rem;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .cta-button:hover {{ 
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            color: var(--teal-dark);
        }}
        
        .back-to-blog {{
            max-width: 750px;
            margin: 0 auto;
            padding: 1.5rem 2rem;
            text-align: center;
            background: var(--white);
        }}
        
        .back-to-blog a {{
            color: var(--teal);
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        .footer {{
            background: var(--charcoal);
            text-align: center;
            padding: 2.5rem 2rem;
            color: rgba(255,255,255,0.6);
            font-size: 0.9rem;
        }}
        
        .footer a {{ 
            color: rgba(255,255,255,0.8); 
        }}
        
        .footer a:hover {{ 
            color: var(--white);
        }}
        
        .footer-links {{
            margin-bottom: 1rem;
            display: flex;
            justify-content: center;
            gap: 2rem;
            flex-wrap: wrap;
        }}
        
        @media (max-width: 768px) {{
            .article-hero {{
                height: 360px;
            }}
            .article-hero h1 {{
                font-size: 1.85rem;
            }}
            .article-container {{
                padding: 2rem 1.5rem;
            }}
        }}
    </style>
</head>
<body>
    <nav class="nav">
        <div class="nav-container">
            <a href="index.html">← Back to Blog</a>
            <a href="{APP_LINKS['website']}">Download SteadiDay</a>
        </div>
    </nav>
    
    <header class="article-hero">
        <div class="article-hero-content">
            <span class="article-tag">{post_data['tag']}</span>
            <h1>{post_data['title']}</h1>
            <div class="article-meta">
                <span>{date_formatted}</span>
                <span>•</span>
                <span>{read_time} min read</span>
                <span>•</span>
                <span>By SteadiDay Team</span>
            </div>
        </div>
    </header>
    
    <article class="article-container">
        <div class="article-content">
            {post_data['content']}
            
            <div class="cta-box">
                <h3>Ready to Take Control of Your Health?</h3>
                <p>SteadiDay helps you manage medications, track your wellness, and build healthy habits—all in one simple app.</p>
                <a href="{APP_LINKS['website']}" class="cta-button">Download SteadiDay Free</a>
            </div>
        </div>
    </article>
    
    <div class="back-to-blog">
        <a href="index.html">← Back to all articles</a>
    </div>
    
    <footer class="footer">
        <div class="footer-links">
            <a href="../index.html">Home</a>
            <a href="../index.html#features">Features</a>
            <a href="../privacy.html">Privacy</a>
            <a href="../terms.html">Terms</a>
        </div>
        <p>© {datetime.now().year} SCM Solutions LLC. All rights reserved. Made with care in Virginia, USA.</p>
    </footer>
</body>
</html>"""
    
    return html


def update_blog_index(post_data: dict):
    """Update the blog index.html with the new post card."""
    
    index_path = "blog/index.html"
    
    if not os.path.exists(index_path):
        print(f"Warning: {index_path} not found, skipping index update")
        return
    
    with open(index_path, 'r', encoding='utf-8') as f:
        index_content = f.read()
    
    date_formatted = datetime.strptime(post_data['date'], '%Y-%m-%d').strftime('%B %d, %Y')
    word_count = len(post_data['content'].split())
    read_time = max(1, round(word_count / 200))
    
    # Create excerpt
    excerpt = re.sub(r'<[^>]+>', '', post_data['content'])[:200]
    excerpt = excerpt.rsplit(' ', 1)[0] + '...'
    
    filename = f"{post_data['date']}-{post_data['slug']}.html"
    
    # New card with stock photo - matches the blog index design
    new_entry = f"""<article class="blog-card">
                <div class="blog-card-image" style="background-image: url('{post_data['photo_url']}');">
                    <span class="blog-card-tag">{post_data['tag']}</span>
                </div>
                <div class="blog-card-content">
                    <h2><a href="{filename}">{post_data['title']}</a></h2>
                    <div class="blog-meta">
                        <span>{date_formatted}</span>
                        <span>•</span>
                        <span>{read_time} min read</span>
                    </div>
                    <p class="blog-excerpt">{excerpt}</p>
                    <a href="{filename}" class="read-more">
                        Read full article
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
                        </svg>
                    </a>
                </div>
            </article>
            
            """
    
    # Insert after marker
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
    print(f"🏷️ Category: {post_data['tag']}")
    print(f"🖼️ Photo: {post_data['photo_url']}")
    
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
