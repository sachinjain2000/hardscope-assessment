# VALORANT Creator Campaign Measurement Workspace
### HardScope Assessment — Lead Analyst, Creator Strategy & ROI

**Author:** Sachin Jain · [sachinjn200@gmail.com](mailto:sachinjn200@gmail.com)  
**Brand:** Riot Games / VALORANT  
**Campaign Period:** Q3 2024 (Jul–Sep) + Q4 2024 (Oct–Dec)  
**Submitted:** April 2026

---

## What This Project Is

A fully reproducible, end-to-end creator measurement workspace that answers a single business question:

> **Which VALORANT YouTube creators delivered the best ROI in Q4 2024, and what should we do differently in Q1 2025?**

It covers every layer of the assessment rubric: real API data pull, a 3-tier measurement framework, feature-engineered analytics, incrementality modelling, a QBR-ready PPTX deck, an executive summary, a Google Sheets dashboard, and a reusable playbook.

---

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/sachinjain2000/hardscope-assessment.git
cd hardscope-assessment

# 2. Install Python dependencies
pip install pandas numpy jupyter pytrends

# 3. (Optional) Re-pull Google Trends data
#    Run from the project root:
python fetch_trends.py

# 4. Run the measurement pipeline
jupyter notebook notebooks/02_measurement_framework.ipynb

# 5. Open the analysis dashboard
jupyter notebook notebooks/03_analysis_dashboard.ipynb
```

> **Note:** `data/raw/` already contains the real YouTube API data (Q3 + Q4) and Google Trends monthly averages fetched during the assessment. Set `REFRESH_DATA = True` at the top of each notebook to re-pull live data.

---

## Project Structure

```
hardscope-assessment/
│
├── data/
│   ├── raw/
│   │   ├── q3_2024_videos.csv          # 55 videos, Jul–Sep 2024 (YouTube API v3)
│   │   ├── q4_2024_videos.csv          # 57 videos, Oct–Dec 2024 (YouTube API v3)
│   │   ├── channel_stats.csv           # Subscriber counts, lifetime stats, tier
│   │   └── search_interest_monthly.csv # Google Trends monthly avg (Jul–Dec 2024)
│   │
│   └── modeled/
│       ├── creator_campaign_metrics.csv  # Master analytics table (21 cols, 14 rows)
│       ├── flagging_alerts.csv           # Automated performance alerts
│       └── incrementality_q3_q4.csv      # Q3→Q4 delta analysis per creator/month
│
├── notebooks/
│   ├── 01_data_collection.ipynb        # YouTube API pull + validation
│   ├── 02_measurement_framework.ipynb  # Feature engineering, joins, modelling
│   └── 03_analysis_dashboard.ipynb     # Plotly charts, leaderboard, trend analysis
│
├── outputs/
│   ├── VALORANT_Creator_QBR_Q3Q4_2024.pptx      # 6-slide QBR deck (includes Methodology slide)
│   ├── Executive_Summary.docx                    # 2-page exec summary (MODELLED flags on CPE)
│   └── VALORANT_Creator_QBR_Dashboard.xlsx       # 5-tab Google Sheets / Excel dashboard
│
├── fetch_trends.py       # Google Trends pull script (run locally)
├── run_pipeline.py       # Single-command measurement pipeline
├── METHODOLOGY.md        # Full replication guide, every decision documented
├── PLAYBOOK.md           # Reusable measurement framework template
└── README.md             # This file
```

---

## Data Sources

### 1. YouTube Data API v3 (Primary)
- **Endpoints used:** `channels`, `search`, `videos`
- **Creators tracked (6):** TenZ, tarik, Kyedae, aceu, Sinatraa, Protatomonster
- **Coverage:** July 1 – December 31, 2024 (112 videos total)
- **Fields captured:** `video_id`, `title`, `published_date`, `views`, `likes`, `comments`, `duration`
- **Why this source:** Authoritative, free, reproducible. No scraping, no third-party aggregators.
- **API quota cost:** ~310 units per full pull (well within 10,000/day free tier)

**To re-pull from the API:**
```javascript
// In Chrome DevTools Console (handles CORS without a server):
const API_KEY = "YOUR_KEY_HERE";
const CHANNEL_ID = "UCckPYr9b_iVucz8ID1Q67sw"; // TenZ example
// See notebooks/01_data_collection.ipynb for full multi-creator pull script
```

### 2. Google Trends (Context Layer)
- **Term:** `valorant` · **Geography:** United States · **Period:** Jul–Dec 2024
- **Tool:** `pytrends` library (local execution — Google blocks server-side scraping)
- **Output:** Weekly interest (0–100 scale), aggregated to monthly averages for joins

**To re-pull:**
```bash
# From project root:
python fetch_trends.py
# Output: data/raw/search_interest.csv (weekly) + search_interest_monthly.csv
```

**Key finding from Trends data:**
- August 2024 peak (77.2) = VCT Champions Seoul tournament
- Q4 average (36.7) vs Q3 average (65.4) — 44% category headwind explains Q4 ER compression

---

## Measurement Framework

Three-layer model mapping creator outputs to business outcomes:

### Layer 1 — Awareness
*"How many people did we reach?"*

| Metric | Formula | Threshold |
|--------|---------|-----------|
| Total Views | Sum of video views | — |
| Views/Day | `views ÷ days_since_publish` | — |
| Reach Index | `views × (1 + ER/100)` | — |
| Search Interest | Google Trends monthly avg | >50 = high season |

### Layer 2 — Engagement
*"Did audiences actually care?"*

| Metric | Formula | Threshold |
|--------|---------|-----------|
| Engagement Rate | `(likes + comments) ÷ views × 100` | ≥3.87% benchmark (Statista 2024) |
| Quality Engagement Index | `(likes + comments×3) ÷ views × 100` | Comments weighted 3× (intent signal) |
| Watch Time (modelled) | `views × duration_seconds × 0.5` | Assumes 50% completion |

### Layer 3 — Consideration
*"Did we move people down the funnel?"*

| Metric | Formula | Threshold |
|--------|---------|-----------|
| Cost Per Engagement (CPE) | `monthly_spend ÷ total_engagements` | ≤$0.11 efficient / ≤$0.25 acceptable |
| CPE Efficiency Tier | `"Efficient" / "Acceptable" / "Review"` | Based on CPE thresholds |
| Incrementality (ΔER) | `Q4_ER − Q3_ER` (pp change) | >0 = improving |

### Budget Model
Spend estimates derived from industry benchmarks (Influencer Marketing Hub 2024):

| Creator | Tier | Est. Monthly Spend |
|---------|------|--------------------|
| TenZ | Macro | $25,000 |
| tarik | Macro | $20,000 |
| Kyedae | Macro | $22,000 |
| aceu | Macro | $28,000 |
| Sinatraa | Mid-Tier | $8,000 |
| Protatomonster | Mid-Tier | $7,000 |

Total Q4 modelled spend: **~$110,000** ⚠ *These are IMH 2024 benchmark estimates, not actual contract rates.*

---

## Feature Engineering

Implemented in `notebooks/02_measurement_framework.ipynb`:

| Feature | Logic |
|---------|-------|
| `content_type` | ISO 8601 duration parse → Short (<2min) / Mid-form (2–20min) / Long-form (>20min) |
| `days_since_publish` | `ANALYSIS_DATE (Jan 15 2025) − published_date` |
| `views_per_day` | Normalized velocity metric |
| `quality_engagement_index` | Comments weighted 3× in engagement score |
| `reach_index` | `views × (1 + er/100)` |
| `watch_time_hrs` | Modelled: `views × duration × 0.5 ÷ 3600` |
| `cpe` | `est_monthly_spend ÷ total_monthly_engagements` |
| `cpe_tier` | "Efficient" / "Acceptable" / "Review" |
| `delta_er` | Q4 ER − Q3 ER (incrementality signal) |
| `is_tenz_viral_outlier` | Flag for TenZ Q3 viral video (7.4M views) |

---

## Three Multi-Source Joins

```
Video data  ──JOIN──▶  channel_stats        (add subscribers, tier)
   │
   ▼
Monthly agg ──JOIN──▶  search_interest      (add Google Trends context)
   │
   ▼
Q4 monthly  ──JOIN──▶  Q3 monthly           (compute ΔER incrementality)
```

---

## Key Findings

### Q4 2024 Program Scorecard
| Metric | Value | Note |
|--------|-------|------|
| Total Views | 7,343,373 | YouTube API — real data |
| Total Engagements | 233,042 | Likes + Comments |
| Blended ER | 3.17% | vs 3.87% benchmark (–18%) |
| Modelled Spend | ~$110,000 | IMH 2024 tier benchmarks — not actual rates |
| Modelled CPE | $0.47 | Spend ÷ Engagements — MODELLED |
| Peak Creator ER | tarik 4.45% | Only improving creator |

### Creator Leaderboard (Q4 ER %)
| Rank | Creator | Q4 ER | Q3→Q4 ΔER | CPE (Est.) | Action |
|------|---------|-------|-----------|-----------|--------|
| 1 | **tarik** | 4.45% | +1.14pp ✅ | $0.20 | SCALE +20% |
| 2 | **TenZ** | 2.93% | –0.65pp | $0.44 ⚠ | MAINTAIN |
| 3 | **Sinatraa** | 2.63% | –1.37pp | $0.86 ⚠ | REDUCE –25% |
| 4 | **aceu** | 2.79% | –0.25pp | $2.42 ⚠ | PAUSE ❌ |
| 5 | **Kyedae** | 2.56% | –1.11pp | $0.53 ⚠ | REDUCE FORMAT |
| 6 | **Protatomonster** | 1.77% | –0.05pp | $0.53 ⚠ | RETIRE / TEST ❌ |

### Q1 2025 Recommendations
| Action | Creator | Rationale |
|--------|---------|-----------|
| SCALE +20% | tarik | Only improving ER; CPE entering Acceptable tier |
| MAINTAIN | TenZ | Largest reach; viral Short was normalised outlier |
| REDUCE FORMAT | Kyedae | CPE overrun 3/3 months; test shorter content |
| REDUCE –25% | Sinatraa | ΔER –1.37pp; CPE overrun every month |
| PAUSE | aceu | CPE $2.42 = worst ROI; reallocate to tarik |
| RETIRE / TEST | Protatomonster | ER 61% below Mid-tier benchmark; no recovery signal |

---

## Automated Alerts

The framework flags four conditions automatically (see `data/modeled/flagging_alerts.csv`):

1. **Declining ER** — MoM drop >0.5 percentage points
2. **High Volume / Low Quality** — Views >500K but ER <2%
3. **Below Platform Average** — ER <50% of 3.87% benchmark (<1.94%)
4. **CPE Overrun** — CPE >$0.25 (acceptable ceiling)

---

## Outputs

| File | Description |
|------|-------------|
| `outputs/VALORANT_Creator_QBR_Dashboard.xlsx` | **5-tab interactive dashboard** (Google Sheets / Excel) |
| `outputs/VALORANT_Creator_QBR_Q3Q4_2024.pptx` | 6-slide QBR deck (incl. Methodology & Limitations slide) |
| `outputs/Executive_Summary.docx` | 2-page narrative for CMO/VP (MODELLED flags on CPE) |
| `data/modeled/creator_campaign_metrics.csv` | Master analytics table, 21 cols, 14 rows |
| `data/modeled/incrementality_q3_q4.csv` | Q3→Q4 delta analysis |
| `data/modeled/flagging_alerts.csv` | Auto-flagged performance issues |

### Opening the Dashboard in Google Sheets

```
1. Download VALORANT_Creator_QBR_Dashboard.xlsx from this repo
2. Go to sheets.google.com → File → Import → Upload the .xlsx file
3. Select "Replace spreadsheet" → Import data
4. The file opens with 5 tabs, auto-filters, and embedded charts
```

> Alternatively, open directly in Excel — all tabs and charts are fully functional.

### Dashboard Tabs

| Tab | Contents |
|-----|----------|
| 📊 Dashboard | Program KPI scorecards, 3-layer funnel actuals, Q1 budget reallocation |
| 🏆 Leaderboard | Sortable creator table (auto-filter on all 15 columns) + Q3/Q4 ER chart |
| 📈 ER Trend | Monthly ER by creator table + trend line chart (4 key creators vs benchmark) |
| ⚡ Incrementality | Q3→Q4 period-over-period delta table + ΔER waterfall bar chart |
| 🚨 Alerts | All 20 automated flags with severity coding + alert summary |

---

## Assumptions & Limitations

1. **Engagement Rate formula:** `(likes + comments) ÷ views × 100`. Shares not available via YouTube API v3 public endpoints.
2. **Watch time is modelled** at 50% average completion — YouTube does not surface this via API for third parties.
3. **Spend estimates** use industry benchmarks (Influencer Marketing Hub 2024), not actual contract rates. Real CPE would differ.
4. **TenZ Q3 viral outlier** (`BiCvVGcuPKE` — 7.4M views, Aug 2024): excluded from Q3 ER baseline for incrementality calculation. Including it inflates Q3 ER to 4.51% vs normalized 3.58%, misleading the Q4 comparison. Flagged in notebook and PPTX.
5. **Google Trends values** are relative (0–100 = peak interest within the pull window), not absolute search volumes. Used for directional context only.
6. **VALORANT Official and VCT Americas** channels included in `channel_stats.csv` for reference but excluded from creator ROI analysis (brand-owned content ≠ creator partnerships).

---

## What I'd Do With Another Week

1. **Pull real spend data** — CPE analysis is only as good as the actual contract rates. Would build a spend ingestion template for the brand/finance team to fill in.
2. **Add Twitter/X and Twitch signals** — YouTube-only view misses where gaming audiences actually spend time. Would pull Twitch VOD data and X impression counts for the same creators.
3. **Sentiment analysis on comments** — 1,000+ comments in the dataset. A simple VADER pass would add a "positive/negative signal" column to the engagement layer.
4. **Creator-level audience overlap** — Are tarik and TenZ reaching the same people? YouTube API doesn't expose this, but a survey or brand lift study would answer it.
5. **Forecasting** — With 6 months of data, a simple linear regression per creator would give Q1 2025 ER projections to set KPI targets.
6. **Automate the pipeline** — Wrap fetch → notebook → PPTX in a GitHub Actions workflow so the QBR deck refreshes automatically before each review.

---

## Reproducibility Checklist

- [x] All raw data files committed to `data/raw/`
- [x] `fetch_trends.py` documented and runnable locally
- [x] YouTube API pull instructions in `notebooks/01_data_collection.ipynb`
- [x] All transformations in notebook cells
- [x] `METHODOLOGY.md` documents every decision with "How to Replicate" sections
- [x] `PLAYBOOK.md` provides a brand-agnostic template for reuse
- [x] Outputs regenerate cleanly from raw data with `jupyter nbconvert --execute`

---

## Dependencies

```
pandas>=1.5
numpy>=1.21
jupyter
plotly>=5.0
pytrends>=4.9
openpyxl>=3.1 (for Dashboard xlsx generation)
python-docx (for Executive_Summary.docx generation)
pptxgenjs (Node.js, for PPTX deck — see outputs/)
```

---
