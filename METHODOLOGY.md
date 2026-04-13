# HardScope Assessment -- Full Methodology & Replication Guide
**Author:** Sachin Jain
**Assessment:** Lead Analyst, Creator Strategy & ROI -- Measurement Challenge
**Brand Chosen:** Riot Games / VALORANT
**Campaign Period:** Q4 2024 (October - December 2024)

---

## How to Use This Document
This file documents every decision, API call, transformation, and assumption made in this project
in enough detail that can be replicated or hand it to a teammate. Each stage ends with a "How to Replicate" section.

---

# STAGE 1 -- Data Collection via YouTube Data API v3

## Why This Data Source?

Using the YouTube Data API v3 is the strongest possible choice because:

- It is the primary, authoritative source -- not a third-party scrape or aggregator
- Every number is directly reproducible by anyone with an API key
- It gives us video-level granularity: views, likes, comments, publish date, duration per video
- It is free (10,000 quota units/day -- more than enough for this analysis)

## Why VALORANT?

- Gaming is the #1 content category on YouTube by volume -> richest available creator data
- Riot Games has a documented Creator Partner Program (launched in closed beta 2024)
- The VALORANT creator ecosystem has clearly defined tiers: macro pros, mid-tier educators, micro entertainers

## Campaign Framing

> Simulated Program: Riot Games VALORANT Q4 2024 Creator Activation
> Objective: Drive player reactivation and new player acquisition around Episode 9 Act 3 launch
> Creators Measured: 6 active YouTube creators across Macro and Mid-Tier segments
> Period: October 1 - December 31, 2024

---

## API Call 1 -- Discover Creator Channels

Endpoint: GET https://www.googleapis.com/youtube/v3/search
Parameters: q="valorant gameplay", type=channel, maxResults=20, order=relevance

Full URL:
https://www.googleapis.com/youtube/v3/search?part=snippet&q=valorant+gameplay&type=channel&maxResults=20&order=relevance&key=YOUR_API_KEY

Quota cost: 100 units

---

## API Call 2 -- Channel Statistics

Endpoint: GET https://www.googleapis.com/youtube/v3/channels
Parameters: part=snippet,statistics, id=[comma-separated channel IDs]

Channel IDs Used:
| Creator | Channel ID |
|---------|-----------|
| TenZ | UCckPYr9b_iVucz8ID1Q67sw |
| tarik | UCTbtlMEiBfs0zZLQyJzR0Uw |
| Kyedae | UCxjdy5n9BxX_6RTL8Dt_7pg |
| aceu | UCBugd2yQNL4TNwHdA56GdnA |
| Sinatraa | UCABUGfcFJhffRFZxSl-mIiw |
| Protatomonster | UCdlvbGGgwfF97wlH7rC8Qng |

Quota cost: 8 units (1 per channel batch)

---

## API Call 3 -- Video Search Per Creator

Endpoint: GET https://www.googleapis.com/youtube/v3/search
Parameters: channelId={id}, publishedAfter=2024-10-01T00:00:00Z,
            publishedBefore=2024-12-31T23:59:59Z, type=video, maxResults=10

Example URL:
https://www.googleapis.com/youtube/v3/search?part=snippet&channelId=UCckPYr9b_iVucz8ID1Q67sw&type=video&publishedAfter=2024-10-01T00:00:00Z&publishedBefore=2024-12-31T23:59:59Z&maxResults=10&key=YOUR_API_KEY

Quota cost: 100 units per call, 600 total for 6 creators

---

## API Call 4 -- Video Statistics

Endpoint: GET https://www.googleapis.com/youtube/v3/videos
Parameters: part=statistics,contentDetails, id={comma-separated video IDs}

Returns: viewCount, likeCount, commentCount (from statistics)
         duration (from contentDetails, ISO 8601 format e.g. PT11M46S)

Quota cost: 1 unit per batch of up to 50 video IDs

---

## Data Collection Results

| Quarter | Videos | Creators | Date Range |
|---------|--------|---------|-----------|
| Q3 2024 | 55 | 5 | Jul-Sep 2024 |
| Q4 2024 | 57 | 6 | Oct-Dec 2024 |
| Total   | 112 | 6 | Jul-Dec 2024 |

## Total API Quota Used

| Call | Units |
|------|-------|
| Channel search | 100 |
| Channel statistics | 8 |
| Video search (x6 creators, 2 quarters) | 1200 |
| Video statistics | 6 |
| Total | ~1314 / 10,000 daily limit |

No cost incurred. Free tier is more than sufficient.

---

## Stage 1 -- Limitations to Disclose

1. Sampled 10 videos per creator per search -- not every video published. A production pipeline
   would paginate and store all video IDs.
2. Views accumulate over time -- recency bias in raw view counts. Addressed in Stage 2 by
   normalizing by days-since-publish.
3. No impression data or CTR -- YouTube only exposes this inside YouTube Studio (requires
   channel owner OAuth). Views used as awareness proxy.
4. No spend data -- Riot's actual creator spend is not public. Modelled from industry benchmarks
   in Stage 2, clearly labelled as "modelled".

---

# STAGE 2 -- Measurement Framework & Feature Engineering

## The 3-Layer Framework

```
Awareness  ->  Engagement  ->  Consideration / ROI
```

This structure maps creator outputs to business outcomes:
- Awareness = reach (easy to inflate, easy to buy)
- Engagement = audience quality (harder to fake)
- Consideration = spend efficiency (requires spend data)

## Feature 1: Duration Parsing -> Content Type

Input: ISO 8601 duration string (e.g. PT11M46S)
Output: Seconds -> Short (<2min) / Mid-form (2-20min) / Long-form (>20min)

```python
def parse_duration_seconds(iso_str):
    h = re.search(r'(\d+)H', iso_str)
    m = re.search(r'(\d+)M', iso_str)
    s = re.search(r'(\d+)S', iso_str)
    return (int(h.group(1)) if h else 0) * 3600 + \
           (int(m.group(1)) if m else 0) * 60 + \
           (int(s.group(1)) if s else 0)
```

## Feature 2: Views/Day (Velocity Normalization)

Analysis date: January 15, 2025 (fixed for reproducibility)

```python
videos['days_since_publish'] = (pd.Timestamp(ANALYSIS_DATE) - videos['published_date']).dt.days
videos['views_per_day'] = (videos['views'] / videos['days_since_publish'].clip(lower=1)).round(1)
```

## Feature 3: Quality Engagement Index (QEI)

```python
qei = (likes + comments * 3) / views * 100
```

The 3x comment weight reflects significantly higher intent vs. likes. Calibrate to your category.

## Feature 4: Reach Index

```python
reach_index = views * (1 + engagement_rate / 100)
```

## Feature 5: Modelled Watch Time

```python
watch_time_hrs = views * duration_seconds * 0.5 / 3600
```

Assumes 50% average completion rate. Conservative; gaming content typically runs 55-65%.

## Feature 6: CPE Tiers

```python
cpe_tier = pd.cut(cpe, bins=[0, 0.11, 0.25, inf], labels=['Efficient', 'Acceptable', 'Review'])
```

## The Three Joins

### Join 1: Video data <- Channel stats (subscribers, tier)
```python
videos = videos.merge(channel_stats[['creator','subscribers','tier']], on='creator', how='left')
```
Provides verified subscriber counts (API returned 0 for Protatomonster in one pull; corrected to 870K).

### Join 2: Monthly aggregates <- Google Trends (search interest)
```python
monthly = monthly.merge(trends[['month','avg_search_interest']], on='month', how='left')
```
Without this column, Q4 ER compression looks like creator failure. It's a 44% category headwind
(Q3 avg 65.4 vs Q4 avg 36.7).

### Join 3: Q4 monthly <- Q3 normalized (incrementality)
```python
incrementality = q3_avg.merge(q4_avg, on='creator')
incrementality['delta_er_pp'] = incrementality['q4_avg_er'] - incrementality['q3_avg_er']
```

**TenZ viral outlier:** The viral Short (7.4M views, Sep 2024) accounts for 78.7% of TenZ's Q3
impressions. Normalized Q3 ER: 3.58% (vs raw 4.51%). The normalized figure is used for
incrementality; the outlier is flagged explicitly.

## How to Replicate Stage 2

```bash
cd hardscope-assessment
python run_pipeline.py
```

Generates:
- data/modeled/creator_campaign_metrics.csv (14 rows x 21 cols)
- data/modeled/incrementality_q3_q4.csv (6 rows)
- data/modeled/flagging_alerts.csv (20 alerts)

---

# STAGE 3 -- Analysis Dashboard

notebooks/03_analysis_dashboard.ipynb covers four Plotly charts:

1. Creator Leaderboard -- Q4 ER bar chart, sorted descending, benchmark line at 3.87%
2. Engagement Trend -- Monthly line chart per creator, Google Trends on secondary Y-axis
3. Incrementality -- Q3 vs Q4 grouped bars, delta ER annotations
4. CPE vs ER Scatter -- aceu visible as outlier, tarik as efficiency leader

---

# STAGE 4 -- QBR Deck

5-slide PPTX (outputs/VALORANT_Creator_QBR_Q3Q4_2024.pptx):
- Slide 1: Title slide -- "Creator ROI Review", KPI summary
- Slide 2: Q4 Program Scorecard -- 6 KPI cards
- Slide 3: Creator Leaderboard -- ER bar chart + ranked table
- Slide 4: Incrementality deep dive -- Q3 vs Q4 grouped bars, 4 finding cards
- Slide 5: Q1 2025 Recommendations -- 5 action cards

VALORANT brand palette: 0F1923 (dark), FF4655 (red), 00B37E (green)

---

# STAGE 5 -- Executive Summary

2-page DOCX (outputs/Executive_Summary.docx):

Page 1: Purpose, Q4 KPI snapshot, market context, creator performance table
Page 2: Measurement framework, key findings, Q1 recommendations, "what next"

---
