# Creator Campaign Measurement Playbook
### A Reusable Framework for Gaming & Entertainment Brand Teams

**Version:** 1.0  
**Based on:** VALORANT Q3–Q4 2024 Creator Campaign Analysis  
**Author:** Sachin Jain

---

## Who This Is For

A brand team, agency, or analyst who needs to measure creator campaigns on YouTube (or any video platform) and answer the question: **"Which creators are driving real business outcomes, and what should we do with next quarter's budget?"**

This playbook is brand-agnostic and platform-agnostic. The VALORANT implementation is the worked example, but the framework applies to any creator program.

---

## The Core Problem This Framework Solves

Most creator measurement stops at reach and engagement rate. That's table stakes. The harder questions are:

- **Are we getting better or worse over time?** (incrementality)
- **Are we spending efficiently?** (CPE benchmarking)
- **Which signals predict future performance?** (leading indicators)
- **When should we act vs. wait?** (automated alerting)

This playbook answers all four.

---

## Part 1: Before You Start — Define What "Good" Looks Like

Before pulling a single data point, align with stakeholders on benchmarks.

### Benchmark Sources (Gaming / Entertainment)

| Metric | Benchmark | Source |
|--------|-----------|--------|
| Engagement Rate (YouTube) | 3.87% | Statista 2024 |
| CPE — Efficient ceiling | $0.11 | Influencer Marketing Hub 2024 |
| CPE — Acceptable ceiling | $0.25 | Influencer Marketing Hub 2024 |
| ER Decline threshold | −0.5pp MoM | Internal heuristic |
| Volume-quality floor | 2.0% ER if views >500K | Internal heuristic |

> **Adapt these for your category.** B2B SaaS creator ER benchmarks are very different from gaming. Always cite your source in the methodology.

### Spend Model (if actual rates unavailable)

Use a tier-based estimate as a placeholder — but flag it as modelled, not actual:

| Creator Tier | Subscriber Range | Estimated Monthly Rate |
|-------------|-----------------|----------------------|
| Macro | 1M+ | $15,000–$30,000 |
| Mid-Tier | 500K–1M | $5,000–$10,000 |
| Micro | 100K–500K | $1,000–$5,000 |
| Nano | <100K | $500–$1,500 |

> **Priority #1 improvement:** Replace these with real contract rates. CPE analysis is only as good as your spend data.

---

## Part 2: Data Architecture

### Required Data Sources

```
Tier 1 — Platform API (primary, authoritative)
├── Video-level metrics: views, likes, comments, duration, publish_date
└── Channel-level metadata: subscribers, lifetime views, tier

Tier 2 — Contextual Signal (mandatory)
└── Search interest (Google Trends or platform search data)
    → Explains category headwinds/tailwinds in ER interpretation

Tier 3 — Financial (for CPE layer)
└── Spend data: actual contract rates or benchmark model
```

### Schema: Raw Video Table

| Column | Type | Source | Notes |
|--------|------|--------|-------|
| `creator` | string | Manual | Creator display name |
| `video_id` | string | YouTube API | Unique identifier |
| `title` | string | YouTube API | |
| `published_date` | date | YouTube API | ISO 8601 |
| `month` | string | Derived | YYYY-MM |
| `views` | int | YouTube API | |
| `likes` | int | YouTube API | |
| `comments` | int | YouTube API | |
| `engagements` | int | Derived | likes + comments |
| `engagement_rate` | float | Derived | engagements / views × 100 |
| `duration` | string | YouTube API | ISO 8601 (PT1H2M3S) |
| `subscribers` | int | Channel API | At time of pull |

### Schema: Master Analytics Table (after pipeline)

| Column | Notes |
|--------|-------|
| `creator` | |
| `month` | YYYY-MM |
| `tier` | Macro / Mid-Tier / Micro |
| `subscribers` | |
| `total_views` | Monthly sum |
| `total_engagements` | Monthly sum |
| `video_count` | Monthly count |
| `engagement_rate` | Monthly blended |
| `quality_engagement_index` | (likes + comments×3) / views × 100 |
| `reach_index` | views × (1 + ER/100) |
| `avg_views_per_day` | Velocity metric |
| `avg_duration_sec` | Content mix signal |
| `total_watch_hrs` | Modelled (50% completion) |
| `est_monthly_spend` | Actual or benchmarked |
| `cpe` | est_spend / engagements |
| `cpe_tier` | Efficient / Acceptable / Review |
| `avg_search_interest` | Google Trends monthly avg |
| `delta_er_pp` | Q4 ER − Q3 ER (incrementality) |
| `trend` | Improving / Flat / Declining |

---

## Part 3: Feature Engineering

### Why Engineer Features?

Raw API metrics tell you **what happened**. Engineered features tell you **why it matters**.

### Feature Catalog

#### Duration → Content Type
```python
def classify_content_type(seconds):
    if seconds < 120:
        return 'Short'       # YouTube Shorts / TikTok-style
    elif seconds <= 1200:
        return 'Mid-form'    # Standard YouTube video
    else:
        return 'Long-form'   # Stream VOD, extended content
```
**Why it matters:** Shorts artificially inflate view counts but depress ER. Compare like-for-like.

#### View Velocity
```python
views_per_day = views / max(days_since_publish, 1)
```
**Why it matters:** A video with 500K views published 2 days ago has very different momentum than one published 6 months ago.

#### Quality Engagement Index
```python
qei = (likes + comments * 3) / views * 100
```
**Why it matters:** Comments require significantly more intent than likes. Weighting them 3× captures audience quality, not just volume. Calibrate the multiplier to your category (games: 3×; beauty: 2×; B2B: 4×).

#### Reach Index
```python
reach_index = views * (1 + engagement_rate / 100)
```
**Why it matters:** Combines reach and resonance into a single sortable number for quick ranking.

#### Modelled Watch Time
```python
watch_time_hrs = views * duration_seconds * 0.5 / 3600
```
**Why it matters:** Platform algorithms reward watch time, not just views. The 0.5 completion assumption is conservative; adjust upward for long-form creators with loyal audiences.

---

## Part 4: The Three-Layer Measurement Framework

```
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 1: AWARENESS                                             │
│  "How many people did we reach, and how fast?"                  │
│                                                                 │
│  → Total Views    → Views/Day     → Reach Index                │
│  → Search Interest (Trends)       → Subscriber Reach %         │
└───────────────────────────┬─────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 2: ENGAGEMENT                                            │
│  "Did audiences care enough to interact?"                       │
│                                                                 │
│  → Engagement Rate    → Quality Engagement Index               │
│  → Watch Time (modelled)   → Comment Sentiment (optional)      │
└───────────────────────────┬─────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 3: CONSIDERATION / ROI                                   │
│  "Are we spending efficiently? Is the investment improving?"    │
│                                                                 │
│  → CPE    → CPE Tier    → ΔER (Incrementality)                 │
│  → Trend (Improving / Flat / Declining)                         │
└─────────────────────────────────────────────────────────────────┘
```

### Connecting Layers to Business Decisions

| Layer | Business Question | Decision Trigger |
|-------|------------------|-----------------|
| Awareness | Are we reaching enough people? | Scale if views/day above tier benchmark |
| Engagement | Is the audience quality good? | Review if QEI <50% of ER benchmark |
| Consideration | Is the spend justified? | Renegotiate if CPE >$0.25; exit if CPE >$1.00 |

---

## Part 5: Incrementality Analysis

### Why This Is the Most Important Metric

Absolute ER in a single quarter tells you performance; ΔER tells you trajectory. A creator at 5% ER falling to 4% is more concerning than one at 3% rising to 3.5%.

### The Approach

1. Establish a **clean Q3 baseline** — remove one-off viral events (define threshold: videos >5× the creator's average views)
2. Compute **average ER per creator per quarter** from monthly data
3. Calculate **ΔER = Q4 avg ER − Q3 avg ER (normalized)**
4. Classify: Improving (>+0.1pp), Flat (±0.1pp), Declining (<−0.1pp)

### Handling Viral Outliers

```
RULE: If a single video accounts for >50% of a creator's quarterly views,
      calculate the baseline ER both with and without it.
      Use the normalized (ex-viral) figure for incrementality comparisons.
      Document and flag the outlier explicitly.
```

---

## Part 6: Automated Alerting

Build four alerts into your reporting pipeline. Flag immediately; do not wait for the QBR.

| Alert | Condition | Action |
|-------|-----------|--------|
| Declining ER | MoM drop >0.5pp | Schedule a creator conversation within 2 weeks |
| High Volume / Low Quality | Views >500K AND ER <2.0% | Review content brief alignment |
| Below Platform Average | ER <50% of category benchmark | Put on watch list; one more cycle to improve |
| CPE Overrun | CPE >$0.25 | Flag for contract review; escalate if >$1.00 |

---

## Part 7: QBR-Ready Deliverables Template

Every creator campaign QBR should ship three complementary outputs:

### A. The Dashboard (Google Sheets / Excel)
The working file a partnerships lead actually opens day-to-day. Must have:

| Tab | Required Content |
|-----|-----------------|
| Dashboard | Program KPI cards + 3-layer funnel scorecard |
| Leaderboard | Sortable creator table (auto-filter on ER, CPE, Tier, Trend) |
| ER Trend | Monthly ER line chart per creator vs benchmark |
| Incrementality | Q3→Q4 delta table + waterfall chart |
| Alerts | Auto-flagged issues with severity codes |

> **Worked example:** `outputs/VALORANT_Creator_QBR_Dashboard.xlsx` — upload to Google Sheets for a shareable link.

### B. The QBR Deck (PPTX / Slides)
Five slides, 90 seconds each to read:

1. **Program Scorecard** — Six KPIs: Views, Engagements, Blended ER, CPE, Spend, Peak ER
2. **Creator Leaderboard** — ER ranked, with ΔER and CPE tier column
3. **Incrementality Slide** — Q3 vs Q4 grouped bar chart, findings called out
4. **Alert Summary** — Flags triggered during the quarter
5. **Recommendations** — One action per creator: Scale / Renew / Renegotiate / Monitor / Rotate

Add a 6th slide for Methodology & Known Limitations — reviewers trust a framework more when its gaps are stated upfront.

### C. The Executive Summary (1–2 pages, DOCX)
Written for the Head of Agency — answers What Happened / What Drove It / What Next in plain English. Keep it under 600 words. Include a MODELLED flag anywhere a number relies on estimates rather than actuals.

Each slide and section should be interpretable in under 90 seconds. If it requires explanation, simplify it.

---

## Part 8: What to Measure Next (Roadmap)

Once the core framework is running, layer in these enhancements in priority order:

### Quarter 1 Enhancement
- **Actual spend data** — Replace benchmark estimates with real contract rates. Nothing else improves CPE accuracy more.

### Quarter 2 Enhancement
- **Comment sentiment** — VADER or a fine-tuned gaming model on the comments corpus. Adds a quality dimension that ER can't capture (high ER with negative sentiment = brand risk).
- **Multi-platform signals** — Pull Twitch concurrent viewers and Twitter/X impressions for the same creators. YouTube-only view systematically understates reach.

### Quarter 3 Enhancement
- **Audience overlap analysis** — Are tarik and TenZ reaching the same people? A survey-based methodology or YouTube analytics export (requires creator cooperation) can answer this.
- **Content type breakdown** — Shorts vs. Mid-form vs. Long-form should have separate ER benchmarks and separate CPE targets.

### Quarter 4 Enhancement
- **Forecasting layer** — 6+ months of weekly data enables simple linear regression per creator for next-quarter ER projections. Set KPI targets before the quarter starts, not after.
- **Pipeline automation** — GitHub Actions workflow: data pull → notebook execution → PPTX generation → Slack delivery, triggered on a schedule or manually pre-QBR.

---

## Part 9: Common Mistakes to Avoid

| Mistake | Why It's a Problem | Fix |
|---------|-------------------|-----|
| Comparing ER across content types | Shorts have 5–10× higher ER than long-form; mixing them misleads | Segment by content_type before aggregating |
| Using viral videos in baseline | Inflates Q3 ER, makes Q4 look worse than it is | Apply viral outlier flag before computing incrementality |
| Ignoring category seasonality | Q4 gaming ER always drops; penalising creators for macro trends is unfair | Add search_interest column to every report |
| Optimising for ER alone | A creator can post one perfectly crafted short to spike ER while delivering no consideration | Require all three layers before making a budget call |
| Using benchmarks without citation | Reviewers will challenge numbers | Always cite source + year for every threshold |
| Waiting for the QBR to flag problems | Issues compound silently between reviews | Build alerting into the weekly pipeline |

---

## Appendix A: API Quick Reference

### YouTube Data API v3

```
Quota: 10,000 units/day (free)
Cost: channels.list = 1 unit; search.list = 100 units; videos.list = 1 unit

Key endpoints:
  GET /channels?part=statistics&id={channelId}
  GET /search?part=snippet&channelId={id}&type=video&publishedAfter={date}&maxResults=50
  GET /videos?part=statistics,contentDetails&id={videoIds}
```

### Google Trends (via pytrends)

```python
from pytrends.request import TrendReq
pt = TrendReq(hl='en-US', tz=360, timeout=(10,30), retries=3, backoff_factor=0.5)
pt.build_payload(kw_list=['valorant'], timeframe='2024-07-01 2024-12-31', geo='US')
df = pt.interest_over_time()
```

---

## Appendix B: Glossary

| Term | Definition |
|------|-----------|
| ER | Engagement Rate = (likes + comments) / views × 100 |
| QEI | Quality Engagement Index = (likes + comments×3) / views × 100 |
| CPE | Cost Per Engagement = monthly_spend / total_engagements |
| ΔER | Delta ER = Q4 avg ER − Q3 avg ER (normalized), in percentage points |
| Reach Index | views × (1 + ER/100) — combined reach + resonance score |
| Viral outlier | A single video contributing >50% of a creator's quarterly views |
| Category headwind | Decline in search interest that depresses ER independently of creator quality |

---
