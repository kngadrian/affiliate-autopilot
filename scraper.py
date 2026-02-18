#!/usr/bin/env python3
"""MunchEye Scraper - Extracts, filters, and scores upcoming launches for Adrian's niches."""

import json, re, subprocess, sys
from datetime import datetime, timedelta
from html import unescape

# Fetch page
result = subprocess.run(
    ['curl', '-s', '--connect-timeout', '10', '--max-time', '15', '-A', 'Mozilla/5.0', 'https://muncheye.com/'],
    capture_output=True, text=True
)
html = result.stdout

# Parse launches from schema.org markup + surrounding HTML
# Pattern: extract each item block
item_pattern = re.compile(
    r"<div class='item\s+clearfix\s*(mega_item)?'>"
    r"(?:.*?title='([^']*)'.*?class='brand'/)?"  # platform
    r".*?<a href='(/[^']+)'[^>]*>([^<]+)</a>"  # url, vendor+name
    r".*?<span class='item_details'>&nbsp;(.*?)</div>"  # price/commission
    r".*?itemprop='name' content='([^']*)'"  # product name
    r".*?itemprop='releaseDate' content='([^']*)'"  # date
    , re.DOTALL
)

today = datetime(2026, 2, 18)
window_start = today
window_end = today + timedelta(days=14)

# Also grab launches in a broader window for better results
# Since today is Feb 18 2026 but MunchEye shows future launches starting from Jun 2026+
# The "next 7-14 days" from the site's perspective - let's take the nearest upcoming launches

launches = []
seen = set()

for m in item_pattern.finditer(html):
    is_mega = bool(m.group(1))
    platform = m.group(2) or 'Unknown'
    url_path = m.group(3)
    vendor_product = unescape(m.group(4))
    price_commission = unescape(m.group(5)).strip()
    product_name = unescape(m.group(6)).strip()
    release_date = m.group(7)
    
    # Parse vendor from vendor_product (format: "Vendor: Product" or "Vendor et al: Product")
    if ':' in vendor_product:
        vendor = vendor_product.split(':')[0].strip()
    else:
        vendor = vendor_product.strip()
    
    # Parse price and commission
    price_match = re.search(r'\$?([\d.]+)', price_commission)
    price = float(price_match.group(1)) if price_match else 0
    comm_match = re.search(r'at\s+(\d+)%', price_commission)
    commission = int(comm_match.group(1)) if comm_match else 50
    
    full_url = f"https://muncheye.com{url_path}"
    
    key = (product_name, release_date)
    if key in seen:
        continue
    seen.add(key)
    
    launches.append({
        'product_name': product_name,
        'vendor': vendor,
        'launch_date': release_date,
        'jv_page_url': full_url,
        'platform': platform,
        'price': price,
        'commission_percent': commission,
        'is_mega_launch': is_mega,
        'price_commission_raw': price_commission,
    })

# Target niches keywords
TARGET_KEYWORDS = [
    'ai', 'artificial intelligence', 'saas', 'builder', 'automation', 'automate',
    'content', 'video', 'creator', 'marketing', 'email', 'funnel', 'seo',
    'social', 'traffic', 'ads', 'agency', 'bot', 'chatbot', 'voice',
    'copy', 'writer', 'blog', 'site', 'web', 'app', 'software',
    'digital', 'prompt', 'gpt', 'clone', 'reel', 'influencer',
    'ebook', 'book', 'publish', 'image', 'design', 'graphic',
    'store', 'ecom', 'market', 'lead', 'inbox', 'mail',
]

STRONG_AI_KEYWORDS = ['ai', 'artificial intelligence', 'gpt', 'prompt', 'chatbot', 'bot', 'clone', 'automation']
SAAS_KEYWORDS = ['saas', 'builder', 'software', 'app', 'platform', 'suite', 'tool']
MARKETING_KEYWORDS = ['marketing', 'funnel', 'email', 'seo', 'traffic', 'ads', 'lead', 'agency']
CONTENT_KEYWORDS = ['content', 'video', 'reel', 'blog', 'ebook', 'book', 'voice', 'image', 'design', 'creator']

def score_launch(launch):
    name_lower = (launch['product_name'] + ' ' + launch['vendor']).lower()
    score = 0
    
    # Niche relevance (0-5)
    ai_hits = sum(1 for k in STRONG_AI_KEYWORDS if k in name_lower)
    saas_hits = sum(1 for k in SAAS_KEYWORDS if k in name_lower)
    marketing_hits = sum(1 for k in MARKETING_KEYWORDS if k in name_lower)
    content_hits = sum(1 for k in CONTENT_KEYWORDS if k in name_lower)
    
    niche_score = min(5, ai_hits * 2 + saas_hits * 1.5 + marketing_hits * 1.5 + content_hits * 1)
    score += niche_score
    
    # Vendor quality (0-2)
    premium_vendors = ['abhi dwivedi', 'karthik ramani', 'ben murray', 'joshua zamora', 
                       'ifiok nkem', 'glynn kosky', 'matt garrett']
    if any(v in launch['vendor'].lower() for v in premium_vendors):
        score += 2
    elif launch['is_mega_launch']:
        score += 2
    elif launch['price'] >= 37:
        score += 1
    
    # Commission (0-1)
    if launch['commission_percent'] >= 50:
        score += 1
    
    # Price point attractiveness (0-1) - higher price = more commission $
    if launch['price'] >= 47:
        score += 1
    elif launch['price'] >= 27:
        score += 0.5
    
    # Cap at 10
    return min(10, round(score))

def classify_niche(launch):
    name_lower = launch['product_name'].lower()
    niches = []
    if any(k in name_lower for k in STRONG_AI_KEYWORDS):
        niches.append('AI Tools')
    if any(k in name_lower for k in SAAS_KEYWORDS):
        niches.append('SaaS')
    if any(k in name_lower for k in MARKETING_KEYWORDS):
        niches.append('Digital Marketing')
    if any(k in name_lower for k in CONTENT_KEYWORDS):
        niches.append('Content Creation')
    if 'automation' in name_lower or 'automate' in name_lower:
        niches.append('Automation')
    return niches if niches else ['General IM']

# Filter for relevant launches
filtered = []
for launch in launches:
    name_lower = (launch['product_name'] + ' ' + launch['vendor']).lower()
    # Must match at least one target keyword
    if any(k in name_lower for k in TARGET_KEYWORDS):
        launch['niche_categories'] = classify_niche(launch)
        launch['score'] = score_launch(launch)
        # Only include if score >= 3 (meaningful relevance)
        if launch['score'] >= 3:
            filtered.append(launch)

# Sort by score desc, then date
filtered.sort(key=lambda x: (-x['score'], x['launch_date']))

# Take top 50 for the dashboard
top_launches = filtered[:50]

# Clean output format
output = []
for l in top_launches:
    output.append({
        'product_name': l['product_name'],
        'vendor': l['vendor'],
        'launch_date': l['launch_date'],
        'jv_page_url': l['jv_page_url'],
        'platform': l['platform'],
        'niche_categories': l['niche_categories'],
        'price_usd': l['price'],
        'commission_percent': l['commission_percent'],
        'is_mega_launch': l['is_mega_launch'],
        'score': l['score'],
    })

# Save JSON
json_path = '/root/.openclaw/workspace/muncheye-launches.json'
with open(json_path, 'w') as f:
    json.dump({
        'scraped_at': '2026-02-18T00:38:00Z',
        'source': 'https://muncheye.com/',
        'total_launches_found': len(launches),
        'filtered_relevant': len(filtered),
        'top_launches': len(output),
        'target_niches': ['AI Tools', 'SaaS', 'Digital Marketing', 'Content Creation', 'Automation'],
        'launches': output,
    }, f, indent=2)

print(f"Total launches parsed: {len(launches)}")
print(f"Filtered relevant: {len(filtered)}")
print(f"Top launches saved: {len(output)}")
print(f"JSON saved to: {json_path}")

# Output for HTML generation
with open('/root/.openclaw/workspace/affiliate-autopilot/launches_data.json', 'w') as f:
    json.dump(output, f, indent=2)
