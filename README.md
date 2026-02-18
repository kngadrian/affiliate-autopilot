# Affiliate Autopilot Dashboard

## Quick Start

```bash
cd /root/.openclaw/workspace/affiliate-autopilot
python3 -m http.server 8080
# Open http://localhost:8080 in your browser
```

## Overview

This dashboard provides a curated view of affiliate product launches from MunchEye, filtered for relevant niches (AI Tools, SaaS, Digital Marketing, Content Creation, Automation). Each launch is scored, and campaign materials can be managed via markdown files.

## Features

- **Live Data Loading:** Launches loaded from `launches_data.json`
- **Campaign Management:** Campaign materials stored as markdown in `campaigns/{product-slug}/`
- **Smart Scoring:** Products scored 1-10 based on niche fit
- **Mega Launch Detection:** Visual indicators for high-potential launches
- **Filter by Niche:** Quick filtering by category
- **Full Campaign Materials:** Brief, bonuses, and email sequences for each campaign

## Data Structure

### Launches Data (`launches_data.json`)

```json
[
  {
    "product_name": "InstaDoodle",
    "vendor": "AdDoodle Media",
    "launch_date": "2026-02-20",
    "jv_page_url": "https://muncheye.com/instadoodle",
    "platform": "JVZoo",
    "niche_categories": ["AI Tools", "Content Creation"],
    "price_usd": 47.0,
    "commission_percent": 50,
    "is_mega_launch": true,
    "score": 9
  }
]
```

### Campaign Materials Directory Structure

```
campaigns/
├── instadoodle/
│   ├── campaign-brief.md       # Strategy, target market, campaign window
│   ├── bonuses.md              # Bonus stack details
│   └── email-sequence.md       # 3-day email sequence
└── {product-slug}/
    ├── campaign-brief.md
    ├── bonuses.md
    └── email-sequence.md
```

### Campaign Brief Format (`campaign-brief.md`)

```markdown
# Campaign Brief — Product Name

**Product:** Product Name
**Platform:** JVZoo
**Target Market:** Target audience description
**Campaign Window:** Time period

## Strategy Summary

Your campaign strategy narrative here...
```

### Bonuses Format (`bonuses.md`)

```markdown
# Custom Bonuses — Product Campaign

## Bonus #1: Bonus Name

**Description:** What the bonus is...

**Perceived Value:** $297

**Why It Complements Product:** Explanation...

---

## Bonus #2: Another Bonus

...
```

### Email Sequence Format (`email-sequence.md`)

```markdown
# 3-Day Email Sequence — Product Campaign

## DAY 1 — Launch Alert / Curiosity Builder

**Subject Line:** Email subject

**Preview Text:** Preview text

**Body:**

Email body content here...

---

## DAY 2 — Demo / Social Proof

...
```

## Adding New Campaigns

1. **Get the product slug:**
   - Convert product name to lowercase
   - Replace spaces and special chars with hyphens
   - Example: "AI AutoBots Pro 2.0" → "ai-autobots-pro-2-0"

2. **Create campaign directory:**
   ```bash
   mkdir -p campaigns/{product-slug}
   ```

3. **Create markdown files:**
   - Copy the InstaDoodle examples as templates
   - Customize for your product

4. **Reload dashboard:**
   - The campaign will be automatically detected and loaded

## How It Works

### Page Load Sequence:
1. Fetch `launches_data.json`
2. Render product cards
3. Update dashboard statistics
4. Background-load campaign materials for each product

### Modal Interaction:
1. User clicks product card
2. Modal opens with product details
3. If campaign exists: Display brief/bonuses/emails
4. If campaign missing: Show "Generate with AI" placeholder

### Markdown Parsing:
- Frontend JavaScript parsers convert markdown to dashboard format
- No build step required
- Handles missing files gracefully

## Files

- `index.html` - Main dashboard (no hardcoded data)
- `launches_data.json` - All product launches
- `campaigns/` - Campaign materials directory
- `scraper.py` - MunchEye scraper (generates launches_data.json)
- `INTEGRATION-COMPLETE.md` - Technical integration details

## Statistics

- **Total Launches:** Loaded from JSON
- **Top Scored:** Count of products with score ≥ 6
- **Avg Score:** Average score across all launches
- **Mega Launches:** Count of `is_mega_launch: true` products

## Development

### Testing Parsers
The markdown parsers can be tested independently:
```javascript
// In browser console on dashboard
const campaign = await loadCampaign('InstaDoodle');
console.log(campaign);
```

### Debugging
- Check browser console for fetch errors
- Verify campaign slug matches directory name
- Ensure markdown files follow the format exactly

## Production Deployment

This is a static dashboard - deploy to any static host:
- GitHub Pages
- Netlify
- Vercel
- S3 + CloudFront

**Note:** Ensure CORS is configured if hosting files on different domains.

## License

Internal tool for Adrian's affiliate marketing operations.
