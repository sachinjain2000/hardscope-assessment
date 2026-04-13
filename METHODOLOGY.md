# HardScope Assessment : Full Methodology & Replication Guide
**Author:** Sachin  
**Assessment:** Lead Analyst, Creator Strategy & ROI — Measurement Challenge  
**Brand Chosen:** Riot Games / VALORANT  
**Campaign Period:** Q4 2024 (October – December 2024)

---

## How to Use This Document

This file documents every decision, API call, transformation, and assumption made in this project — in enough detail that you can replicate each step manually or hand it to a teammate. 

---

# STAGE 1 : Data Collection via YouTube Data API v3

## Why This Data Source?

The assessment asks for data from a "legitimate source" and lists **platform APIs** as the top example. Using the YouTube Data API v3 is the strongest possible choice because:

- It is the **primary, authoritative source** — not a third-party scrape or aggregator
- Every number is **directly reproducible** by anyone with an API key
- It gives us **video-level granularity**: views, likes, comments, publish date, duration per video
- It is **free** (10,000 quota units/day — more than enough for this analysis)
- It shows **resourcefulness**: you went to the source, not to a pre-packaged dataset

## Why VALORANT?

- Gaming is the **#1 content category on YouTube** by volume → richest available creator data
- Riot Games has a documented **Creator Partner Program** (launched in closed beta 2024) → this is a real, named program, not a hypothetical
- The VALORANT creator ecosystem has clearly defined **tiers of creators** (macro pros, mid-tier educators, micro entertainers) → ideal for a multi-tier measurement framework
- HardScope focuses on creator ROI for media brands — gaming brands are a primary client archetype

## Campaign Framing

> **Simulated Program:** Riot Games VALORANT Q4 2024 Creator Activation  
> **Objective:** Drive player reactivation and new player acquisition around Episode 9 Act 3 launch  
> **Creators Measured:** 6 active YouTube creators across Macro and Mid-Tier segments  
> **Period:** October 1 – December 31, 2024

---

## API Call 1 : Discover Creator Channels

**Purpose:** Confirm which channels are actively producing VALORANT content in 2024.

**Endpoint:**
```
GET https://www.googleapis.com/youtube/v3/search
```

**Parameters:**
```
q             = "valorant gameplay"
type          = channel
maxResults    = 20
order         = relevance
key           = YOUR_API_KEY
```

**Full URL (paste into browser or curl):**
```
https://www.googleapis.com/youtube/v3/search?part=snippet&q=valorant+gameplay&type=channel&maxResults=20&order=relevance&key=YOUR_API_KEY
```

**How to replicate manually:**
1. Go to https://console.cloud.google.com
2. Create a project → Enable "YouTube Data API v3" → Create an API Key
3. Paste the URL above into your browser (replace YOUR_API_KEY)
4. You'll get a JSON response — look for `items[].snippet.channelId` and `items[].snippet.channelTitle`

**What we got:**
- 20 channels including: Rawzu, Valorant DAILY, VALORANT Pro Player POVs, Protatomonster, tarik, Sinatraa, VCT Americas, and others
- Used this to **confirm the active creator landscape** and select targets for deeper analysis

**Quota cost:** 100 units (1 search call)

---

## API Call 2 : Channel Statistics (Real Subscriber + View Counts)

**Purpose:** Get ground-truth subscriber counts, lifetime view totals, and video counts for our selected creators.

**Endpoint:**
```
GET https://www.googleapis.com/youtube/v3/channels
```

**Channel IDs Used:**
| Creator | Channel ID |
|---|---|
| TenZ | UCckPYr9b_iVucz8ID1Q67sw |
| tarik | UCTbtlMEiBfs0zZLQyJzR0Uw |
| Kyedae | UCxjdy5n9BxX_6RTL8Dt_7pg |
| aceu | UCBugd2yQNL4TNwHdA56GdnA |
| Sinatraa | UCABUGfcFJhffRFZxSl-mIiw |
| Protatomonster | UCdlvbGGgwfF97wlH7rC8Qng |
| VALORANT Official | UC8CX0LD98EDXl4UYX1MDCXg |
| VCT Americas | UCifCesg-EUkjKyQedaB3hRg |

**Real data returned (verified live, April 2026):**

| Creator | Subscribers | Lifetime Views | Videos |
|---|---|---|---|
| TenZ | 2,720,000 | 415,290,284 | 1,018 |
| tarik | 1,020,000 | 488,883,725 | 2,387 |
| Kyedae | 1,460,000 | 377,997,382 | 267 |
| aceu | 1,830,000 | 414,683,273 | 1,086 |
| Sinatraa | 512,000 | 159,902,146 | 987 |
| Protatomonster | 870,000 | 629,488,990 | 2,527 |
| VALORANT Official | 2,890,000 | 864,441,384 | 664 |
| VCT Americas | 284,000 | 94,852,014 | 2,423 |

**Quota cost:** 8 units (1 unit per channel)

---

## API Call 3 : Q4 2024 Video IDs Per Creator

**Purpose:** Find all videos each creator published between October 1 and December 31, 2024.

**Full URL example for TenZ:**
```
https://www.googleapis.com/youtube/v3/search?part=id&channelId=UCckPYr9b_iVucz8ID1Q67sw&type=video&order=date&publishedAfter=2024-10-01T00:00:00Z&publishedBefore=2024-12-31T23:59:59Z&maxResults=20&key=YOUR_API_KEY
```

**What we got:**
| Creator | Q4 2024 Videos Found |
|---|---|
| TenZ | 10 (sampled from 20+) |
| tarik | 10 (sampled from 20+) |
| Kyedae | 10 (sampled from 20+) |
| aceu | 7 (lower output in Q4) |
| Sinatraa | 10 (sampled from 20+) |
| Protatomonster | 10 (sampled from 20+) |

**Quota cost:** ~100 units per creator × 6 = ~600 units

---

## API Call 4 : Video-Level Statistics (Views, Likes, Comments)

**Purpose:** Get the actual performance numbers for each video — the core dataset.

**Endpoint:**
```
GET https://www.googleapis.com/youtube/v3/videos?part=statistics,snippet,contentDetails&id=[VIDEO_IDs]&key=YOUR_API_KEY
```

**Summary by creator (Q4 2024):**

| Creator | Tier | Q4 Videos | Total Views | ER% |
|---|---|---|---|---|
| TenZ | Macro | 10 | 1,919,571 | 2.93% |
| tarik | Macro | 10 | 2,296,493 | **4.45%** |
| Kyedae | Macro | 10 | 1,619,831 | 2.56% |
| aceu | Macro | 7 | 413,863 | 2.79% |
| Sinatraa | Mid-Tier | 10 | 354,135 | 2.63% |
| Protatomonster | Mid-Tier | 10 | 739,340 | 1.77% |

**Quota cost:** ~6 units (1 per batch of 50 videos)

---

## Stage 1 : Total API Quota Used

| Call | Units Used |
|---|---|
| Channel search | 100 |
| Channel statistics | 8 |
| Video search (×6 creators) | 600 |
| Video statistics | 6 |
| **Total** | **~714 / 10,000 daily limit** |

No cost incurred. Free tier is more than sufficient.

---

## Stage 1 : Limitations

1. **We sampled 10 videos per creator** — not every video they posted in Q4. For production, paginate and store all video IDs.
2. **Views accumulate over time** — a video posted Oct 1 has had 3 months to accumulate views; one posted Dec 30 has had days. Normalized by views/day in Stage 2.
3. **We don't have impression data or CTR** — only accessible inside YouTube Studio (requires channel owner OAuth).
4. **No spend data** — Riot's actual creator spend is not public. Modelled from IMH 2024 benchmarks, clearly labelled.

---

# STAGE 2 : Measurement Framework & Feature Engineering

## The 3-Layer Framework

```
Awareness  →  Engagement  →  Consideration / ROI
```

## Feature 1: Duration Parsing → Content Type

```python
def parse_duration_seconds(iso_str):
    h = re.search(r'(\d+)H', iso_str)
    m = re.search(r'(\d+)M', iso_str)
    s = re.search(r'(\d+)S', iso_str)
    return (int(h.group(1)) if h else 0) * 3600 + \
           (int(m.group(1)) if m else 0) * 60 + \
           (int(s.group(1)) if s else 0)

def classify_content_type(seconds):
    if seconds < 120:    return 'Short'
    elif seconds <= 1200: return 'Mid-form'
    else:                 return 'Long-form'
```

## Feature 2: Views/Day (Velocity Normalization)

```python
ANALYSIS_DATE = date(2025, 1, 15)
videos['days_since_publish'] = (pd.Timestamp(ANALYSIS_DATE) - videos['published_date']).dt.days
videos['views_per_day'] = (videos['views'] / videos['days_since_publish'].clip(lower=1)).round(1)
```

## Feature 3: Quality Engagement Index (QEI)

```python
qei = (likes + comments * 3) / views * 100
```

Comments weighted 3× — requires significantly more intent than a passive like.

## Feature 4: Reach Index

```python
reach_index = views * (1 + engagement_rate / 100)
```

## Feature 5: Modelled Watch Time

```python
watch_time_hrs = views * duration_seconds * 0.5 / 3600
```

Assumes 50% average completion rate. Conservative; flag in any presentation.

## Feature 6: CPE Tiers

```python
cpe_tier = pd.cut(cpe, bins=[0, 0.11, 0.25, float('inf')],
                  labels=['Efficient', 'Acceptable', 'Review'])
```

| Tier | CPE Range | Action |
|------|-----------|--------|
| Efficient | ≤$0.11 | Scale |
| Acceptable | $0.11–$0.25 | Renew |
| Review | >$0.25 | Renegotiate or exit |

## Feature 7: Tier-Adjusted ER Benchmarks

```python
TIER_ER_BENCHMARKS = {'Mega': 2.0, 'Macro': 3.0, 'Mid': 4.5, 'Micro': 6.0}
agg['tier_er_benchmark'] = agg['tier'].map(TIER_ER_BENCHMARKS).fillna(3.87)
agg['er_vs_tier_benchmark'] = (agg['engagement_rate'] / agg['tier_er_benchmark']).round(3)
```

---

## The Three Joins

### Join 1: Video data ← Channel stats
```python
videos = videos.merge(channel_stats[['creator','subscribers','tier']], on='creator', how='left')
```

### Join 2: Monthly aggregates ← Google Trends
```python
monthly = monthly.merge(trends[['month','avg_search_interest']], on='month', how='left')
```
**Why:** Q4 search interest dropped 44% vs Q3 (65.4 → 36.7). Without this column, a reviewer would incorrectly attribute the ER compression entirely to creator failure.

### Join 3: Q4 monthly ← Q3 normalized (incrementality)
```python
incrementality = q3_avg.merge(q4_avg, on='creator')
incrementality['delta_er_pp'] = incrementality['q4_avg_er'] - incrementality['q3_avg_er']
```

**TenZ viral outlier handling:** The viral Short (`BiCvVGcuPKE`, 7.4M views) accounts for 78.7% of TenZ's Q3 impressions. Q3 ER raw = 4.51%; normalized (ex-viral) = 3.58%. Normalized figure used for incrementality. Outlier flagged explicitly in PPTX and DOCX.

---

## How to Replicate Stage 2

```bash
python run_pipeline.py
```

Outputs:
- `data/modeled/creator_campaign_metrics.csv` (14 rows × 21 cols)
- `data/modeled/incrementality_q3_q4.csv` (6 rows)
- `data/modeled/flagging_alerts.csv` (20 alerts)

---

# STAGE 3 : Analysis Dashboard

## Deliverables

| File | Tool | When to Use |
|------|------|-------------|
| `outputs/VALORANT_Creator_QBR_Dashboard.xlsx` | Excel / Google Sheets | Shareable link for stakeholders |
| `notebooks/03_analysis_dashboard.ipynb` | Jupyter + Plotly | Interactive exploration with hover tooltips |

**Opening the xlsx in Google Sheets:** sheets.google.com → File → Import → Upload → select .xlsx → "Replace spreadsheet". All 5 tabs, auto-filters, and charts render correctly.

## xlsx Dashboard: 5 Tabs

| Tab | Contents |
|-----|----------|
| 📊 Dashboard | Program KPI cards, 3-layer funnel scorecard (with confidence levels), Q1 budget reallocation |
| 🏆 Leaderboard | All 6 creators × 15 KPIs, auto-filter, Q3 vs Q4 ER bar chart |
| 📈 ER Trend | Monthly ER by creator table + line chart (TenZ/tarik/Kyedae vs benchmark) |
| ⚡ Incrementality | Q3→Q4 delta table + ΔER waterfall chart + tier-adjusted benchmark comparison |
| 🚨 Alerts | All 20 automated flags with 🔴/🟡/🟢 severity coding and alert summary counts |

## What's in Notebook 03

`notebooks/03_analysis_dashboard.ipynb` uses Plotly to generate 5 interactive charts:
1. Creator Leaderboard (Q4 ER bar chart, benchmark line)
2. Monthly ER Trend (line chart, Google Trends overlay on secondary axis)
3. Incrementality Bar Chart (Q3 vs Q4 grouped, ΔER annotations)
4. CPE vs ER Scatter Plot (quadrant lines at ER=3.87% and CPE=$0.25)
5. Flagging Alerts Summary

```bash
jupyter notebook notebooks/03_analysis_dashboard.ipynb
```

---

# STAGE 4 : QBR Deck

## Slide Architecture

The 6-slide PPTX (`outputs/VALORANT_Creator_QBR_Q3Q4_2024.pptx`) is built with PptxGenJS:

| Slide | Title | Purpose |
|-------|-------|---------|
| 1 | Title | Campaign context, period, one-line KPI |
| 2 | Q4 Program Scorecard | Six KPI cards — Views, Engagements, ER, Spend, CPE, Peak ER |
| 3 | Creator Leaderboard | ER bar chart + ranked table with CPE tier |
| 4 | Incrementality Deep Dive | Q3 vs Q4 grouped bar chart, 4 findings |
| 5 | Q1 2025 Recommendations | One action per creator with rationale |
| 6 | Methodology & Known Limitations | Left: what's defensible. Right: 5 known gaps |

Slide 6 is a deliberate addition — reviewers trust a framework more when its limitations are stated upfront rather than surfaced in Q&A.

---

# STAGE 5 : Executive Summary

The executive summary (`outputs/Executive_Summary.docx`) is a 2-page narrative for a CMO or Head of Agency who won't open the deck. Answers five questions:

1. What did we set out to do?
2. What did we spend? *(with MODELLED flag on all CPE figures)*
3. What worked?
4. What didn't, and why?
5. What should we do next?

Every CPE figure in the DOCX is flagged with ⚠ MODELLED. Section 6 "Known Limitations" mirrors METHODOLOGY.md Stage 6 in condensed form.

---

# STAGE 6 : Known Limitations & Honest Assessment

This stage documents what the framework **cannot** claim, and what evidence would be required to make stronger assertions.

---

## Limitation 1: ΔER Is Not Causal Incrementality

**What we measure:** Period-over-period change in engagement rate (Q4 ER − Q3 ER).

**What we claim:** "tarik is the only creator showing improvement" — directionally correct.

**What we cannot claim:** That tarik's +1.14pp ΔER was caused by the creator partnership. Alternative explanations: algorithm tailwind, VCT tournament content, audience mix shift, or content format change.

**What would prove it:** A geo-holdout test or propensity score matched market design.

**How to communicate this:** Describe ΔER as a "directional performance signal" or "period-over-period proxy." Never call it "incremental lift" or "causal ROI."

---

## Limitation 2: CPE Is Fully Modelled — No Actual Spend Data

**The spend estimates:**

| Creator | Tier | Est. Monthly Spend | Source |
|---------|------|-------------------|--------|
| TenZ | Macro | $25,000 | IMH 2024 Macro benchmark midpoint |
| tarik | Macro | $20,000 | IMH 2024 Macro benchmark low-end |
| Kyedae | Macro | $22,000 | IMH 2024 Macro benchmark |
| aceu | Macro | $28,000 | IMH 2024 Macro benchmark high-end |
| Sinatraa | Mid-Tier | $8,000 | IMH 2024 Mid-Tier benchmark |
| Protatomonster | Mid-Tier | $7,000 | IMH 2024 Mid-Tier benchmark low-end |

**What we cannot claim:** That aceu's CPE of $2.42 is real. It could be $0.50 or $5.00 depending on actual contract rates.

**What would fix it:** A spend ingestion template filled in by the brand partnerships team.

---

## Limitation 3: Tier-Adjusted Benchmarks

**Tier-adjusted benchmarks applied in run_pipeline.py:**

| Tier | Expected ER | Source |
|------|------------|--------|
| Mega (5M+ subs) | 2.0% | IMH 2024 |
| Macro (1M–5M) | 3.0% | IMH 2024 |
| Mid-Tier (500K–1M) | 4.5% | IMH 2024 |
| Micro (<500K) | 6.0% | IMH 2024 |

Protatomonster's 1.77% looks even worse against the 4.5% Mid-Tier benchmark (–61%) than against the global 3.87% (–54%). The leaderboard ranking is robust either way.

---

## Limitation 4: Watch Time Completion Rate Assumed at 50%

Shorts typically complete at 85–95%; long-form VODs at 10–20%. Total watch time numbers should be treated as order-of-magnitude estimates. Real completion rates require YouTube Analytics OAuth access per creator channel.

---

## Limitation 5: No Lower-Funnel Signals

Missing from the Consideration layer:
- Link-in-bio clicks (requires Linktree/Beacons API)
- Discount code redemptions (requires brand partnership data)
- Game downloads / player reactivation (requires Riot's internal attribution model)
- Brand lift / purchase intent survey

---

