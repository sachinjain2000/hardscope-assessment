# Creator Campaign Measurement Playbook
### A Reusable Framework for Gaming & Entertainment Brand Teams

**Version:** 1.0
**Based on:** VALORANT Q3-Q4 2024 Creator Campaign Analysis
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

## Part 1: Before You Start -- Define What "Good" Looks Like

Before pulling a single data point, align with stakeholders on benchmarks.

### Benchmark Sources (Gaming / Entertainment)

| Metric | Benchmark | Source |
|--------|-----------|--------|
| Engagement Rate (YouTube) | 3.87% | Statista 2024 |
| CPE -- Efficient ceiling | $0.11 | Influencer Marketing Hub 2024 |
| CPE -- Acceptable ceiling | $0.25 | Influencer Marketing Hub 2024 |
| ER Decline threshold | -0.5pp MoM | Internal heuristic |
| Volume-quality floor | 2.0% ER if views >500K | Internal heuristic |

> **Adapt these for your category.** B2B SaaS creator ER benchmarks are very different from gaming. Always cite your source in the methodology.

### Spend Model (if actual rates unavailable)

| Creator Tier | Subscriber Range | Estimated Monthly Rate |
|-------------|-----------------|----------------------|
| Macro | 1M+ | $15,000-$30,000 |
| Mid-Tier | 500K-1M | $5,000-$10,000 |
| Micro | 100K-500K | $1,000-$5,000 |
| Nano | <100K | $500-$1,500 |

> **Priority #1 improvement:** Replace these with real contract rates. CPE analysis is only as good as your spend data.

---

## Part 2: Data Architecture

### Required Data Sources

```
Tier 1 -- Platform API (primary, authoritative)
  Video-level metrics: views, likes, comments, duration, publish_date
  Channel-level metadata: subscribers, lifetime views, tier

Tier 2 -- Contextual Signal (mandatory)
  Search interest (Google Trends or platform search data)
  Explains category headwinds/tailwinds in ER interpretation

Tier 3 -- Financial (for CPE layer)
  Spend data: actual contract rates or benchmark model
```

### Schema: Raw Video Table

| Column | Type | Source | Notes |
|--------|------|--------|-------|
| creator | string | Manual | Creator display name |
| video_id | string | YouTube API | Unique identifier |
| title | string | YouTube API | |
| published_date | date | YouTube API | ISO 8601 |
| month | string | Derived | YYYY-MM |
| views | int | YouTube API | |
| likes | int | YouTube API | |
| comments | int | YouTube API | |
| engagements | int | Derived | likes + comments |
| engagement_rate | float | Derived | engagements / views * 100 |
| duration | string | YouTube API | ISO 8601 (PT1H2M3S) |
| subscribers | int | Channel API | At time of pull |

---

## Part 3: Feature Engineering

### Feature Catalog

#### Duration -> Content Type
```python
def classify_content_type(seconds):
    if seconds < 120:    return 'Short'      # YouTube Shorts
    elif seconds <= 1200: return 'Mid-form'  # Standard video
    else:                 return 'Long-form' # Stream VOD
```
**Why it matters:** Shorts inflate view counts but depress ER. Compare like-for-like.

#### View Velocity
```python
views_per_day = views / max(days_since_publish, 1)
```

#### Quality Engagement Index
```python
qei = (likes + comments * 3) / views * 100
```
**Why it matters:** Comments require more intent than likes. 3x weight captures audience quality. Calibrate to your category (games: 3x; B2B: 4x).

#### Reach Index
```python
reach_index = views * (1 + engagement_rate / 100)
```

#### Modelled Watch Time
```python
watch_time_hrs = views * duration_seconds * 0.5 / 3600
```

---

## Part 4: The Three-Layer Measurement Framework

```
LAYER 1: AWARENESS
  "How many people did we reach, and how fast?"
  -> Total Views  -> Views/Day  -> Reach Index  -> Search Interest

LAYER 2: ENGAGEMENT
  "Did audiences care enough to interact?"
  -> Engagement Rate  -> Quality Engagement Index  -> Watch Time

LAYER 3: CONSIDERATION / ROI
  "Are we spending efficiently? Is the investment improving?"
  -> CPE  -> CPE Tier  -> Delta ER (Incrementality)  -> Trend
```

### Connecting Layers to Business Decisions

| Layer | Business Question | Decision Trigger |
|-------|------------------|-----------------|
| Awareness | Are we reaching enough people? | Scale if views/day above tier benchmark |
| Engagement | Is the audience quality good? | Review if QEI <50% of ER benchmark |
| Consideration | Is the spend justified? | Renegotiate if CPE >$0.25; exit if CPE >$1.00 |

---

## Part 5: Incrementality Analysis

Absolute ER in a single quarter tells you performance; delta ER tells you trajectory. A creator at 5% ER falling to 4% is more concerning than one at 3% rising to 3.5%.

### The Approach

1. Establish a clean Q3 baseline -- remove viral outliers (videos >5x creator's average views)
2. Compute average ER per creator per quarter
3. Calculate delta ER = Q4 avg ER - Q3 avg ER (normalized)
4. Classify: Improving (>+0.1pp), Flat (+-0.1pp), Declining (<-0.1pp)

### Viral Outlier Rule
```
If a single video accounts for >50% of a creator's quarterly views:
  - Calculate baseline ER both with and without it
  - Use normalized (ex-viral) figure for incrementality
  - Document and flag the outlier explicitly
```

---

## Part 6: Automated Alerting

| Alert | Condition | Action |
|-------|-----------|--------|
| Declining ER | MoM drop >0.5pp | Creator conversation within 2 weeks |
| High Volume / Low Quality | Views >500K AND ER <2.0% | Review content brief |
| Below Platform Average | ER <50% of benchmark | Watch list; one more cycle |
| CPE Overrun | CPE >$0.25 | Contract review; escalate if >$1.00 |

---

## Part 7: QBR-Ready Deliverables Template

Every QBR needs five components:
1. **Program Scorecard** -- Six KPIs: Views, Engagements, Blended ER, CPE, Spend, Peak ER
2. **Creator Leaderboard** -- ER ranked, with delta ER and CPE tier
3. **Incrementality Slide** -- Q3 vs Q4 grouped bar chart, findings called out
4. **Alert Summary** -- Flags triggered during the quarter
5. **Recommendations** -- One action per creator: Scale / Renew / Renegotiate / Monitor / Rotate

---

## Part 8: Enhancement Roadmap

**Q1:** Connect actual spend data (replaces benchmark estimates)
**Q2:** Comment sentiment (VADER) + multi-platform signals (Twitch, Twitter/X)
**Q3:** Audience overlap analysis + content type benchmarks
**Q4:** Forecasting layer (linear regression per creator) + pipeline automation

---

## Part 9: Common Mistakes

| Mistake | Fix |
|---------|-----|
| Comparing ER across content types | Segment by content_type first |
| Using viral videos in baseline | Apply outlier flag before incrementality |
| Ignoring category seasonality | Add search_interest to every report |
| Optimising for ER alone | Require all 3 layers before budget decision |
| Benchmarks without citation | Always cite source + year |
| Waiting for QBR to flag problems | Build weekly alerting pipeline |

---

## Appendix A: API Quick Reference

### YouTube Data API v3
```
Quota: 10,000 units/day (free)
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
Note: pytrends 4.9.2 + urllib3 2.x requires method_whitelist->allowed_methods patch. See fetch_trends.py.

---

## Appendix B: Glossary

| Term | Definition |
|------|-----------|
| ER | Engagement Rate = (likes + comments) / views * 100 |
| QEI | Quality Engagement Index = (likes + comments*3) / views * 100 |
| CPE | Cost Per Engagement = monthly_spend / total_engagements |
| Delta ER | Q4 avg ER - Q3 avg ER (normalized), in percentage points |
| Reach Index | views * (1 + ER/100) -- combined reach + resonance score |
| Viral outlier | A single video contributing >50% of creator's quarterly views |
| Category headwind | Decline in search interest depressing ER independently of creator quality |

---

*This playbook was built for the HardScope Lead Analyst assessment and is designed to be hand-off-ready for a brand or agency team.*
