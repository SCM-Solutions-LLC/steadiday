"""Credit the sources a post links to: a visible "Sources" list at the end of
the article and a schema.org "citation" list in the Article JSON-LD.

Only links already in the post body are listed. Nothing is looked up or added,
so the list can never cite something the article does not.

Shared by generate_blog.py (new posts) and backfill_sources.py (published
posts). Kept free of the anthropic import so the backfill runs anywhere.
"""
import json
import re
from html import escape, unescape
from urllib.parse import urlparse

# Links that are not sources: our own site, the App Store, images, analytics.
NOT_SOURCES = ("steadiday.com", "apps.apple.com", "unsplash.com",
               "googletagmanager.com", "fonts.googleapis.com", "fonts.gstatic.com")

PUBLISHERS = {
    "pubmed.ncbi.nlm.nih.gov": "PubMed", "pmc.ncbi.nlm.nih.gov": "PubMed Central",
    "www.ncbi.nlm.nih.gov": "NCBI (NIH)", "www.nih.gov": "NIH", "www.nia.nih.gov": "National Institute on Aging",
    "www.nccih.nih.gov": "NCCIH (NIH)", "www.ninds.nih.gov": "NINDS (NIH)",
    "www.cdc.gov": "CDC", "wwwnc.cdc.gov": "CDC", "www.fda.gov": "FDA", "www.who.int": "World Health Organization",
    "jamanetwork.com": "JAMA Network", "www.nejm.org": "New England Journal of Medicine",
    "www.thelancet.com": "The Lancet", "www.nature.com": "Nature", "www.health.harvard.edu": "Harvard Health",
    "www.mayoclinic.org": "Mayo Clinic", "cancerblog.mayoclinic.org": "Mayo Clinic", "www.aarp.org": "AARP",
    "alz-journals.onlinelibrary.wiley.com": "Alzheimer's & Dementia", "www.alz.org": "Alzheimer's Association",
    "www.uspreventiveservicestaskforce.org": "US Preventive Services Task Force", "www.acc.org": "American College of Cardiology",
    "newsroom.heart.org": "American Heart Association", "www.aafp.org": "American Academy of Family Physicians",
    "www.usfa.fema.gov": "US Fire Administration", "www.nfpa.org": "NFPA", "www.nhtsa.gov": "NHTSA",
    "journals.plos.org": "PLOS", "www.neurology.org": "Neurology", "pubs.rsna.org": "RSNA",
    "www.federalregister.gov": "Federal Register", "doi.org": "DOI", "www.sciencedirect.com": "ScienceDirect",
    "www.frontiersin.org": "Frontiers",
    "bjsm.bmj.com": "British Journal of Sports Medicine", "bmcpsychiatry.biomedcentral.com": "BMC Psychiatry",
    "www.jvir.org": "Journal of Vascular and Interventional Radiology", "www.pharmacytimes.com": "Pharmacy Times",
    "www.kctv5.com": "KCTV5 News", "www.eisai.com": "Eisai", "www.shionogi.com": "Shionogi",
}

LINK = re.compile(r'<a\s[^>]*href="(https?://[^"]+)"[^>]*>(.*?)</a>', re.S)


def extract_sources(content_html):
    """[(url, linked text)] for each distinct external link, in reading order."""
    seen, out = set(), []
    for url, text in LINK.findall(content_html):
        url = unescape(url)
        host = urlparse(url).netloc.lower()
        if any(host == d or host.endswith("." + d) for d in NOT_SOURCES) or url in seen:
            continue
        seen.add(url)
        out.append((url, " ".join(unescape(re.sub(r"<[^>]+>", "", text)).split())))
    return out


def publisher(url):
    host = urlparse(url).netloc.lower()
    return PUBLISHERS.get(host, host.removeprefix("www."))


def render_sources_block(sources):
    if not sources:
        return ""
    items = "".join(
        f'<li><a href="{escape(u)}" target="_blank" rel="noopener">{escape(publisher(u))}</a>'
        + (f': &ldquo;{escape(t)}&rdquo;' if t else "") + "</li>"
        for u, t in sources)
    return ('<section class="post-sources" aria-labelledby="sources-heading">'
            '<h2 id="sources-heading">Sources</h2>'
            '<p>This article draws on the sources below. Each entry shows the passage it supports.</p>'
            f'<ol>{items}</ol></section>')


def citation_jsonld(sources):
    """'"citation":[...],' ready to sit before "mainEntityOfPage", or ''."""
    return f'"citation":{json.dumps([u for u, _ in sources])},' if sources else ""


if __name__ == "__main__":
    s = extract_sources('<a href="https://www.cdc.gov/x">a &amp; b</a> <a href="https://www.cdc.gov/x">dup</a>'
                        '<a href="https://www.steadiday.com/y">own</a><a href="https://apps.apple.com/z">app</a>')
    assert s == [("https://www.cdc.gov/x", "a & b")], s
    assert "CDC</a>: &ldquo;a &amp; b&rdquo;" in render_sources_block(s)
    assert json.loads("{" + citation_jsonld(s)[:-1] + "}")["citation"] == ["https://www.cdc.gov/x"]
    assert render_sources_block([]) == citation_jsonld([]) == ""
    print("ok")
