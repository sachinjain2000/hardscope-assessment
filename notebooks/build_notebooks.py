"""
Helper script — builds all three Jupyter notebooks from cell definitions.
Run once: python build_notebooks.py
"""
import nbformat as nbf
import os

os.makedirs("../notebooks", exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# NOTEBOOK 1 — Data Collection
# ─────────────────────────────────────────────────────────────────────────────
nb1 = nbf.v4.new_notebook()
nb1.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}}

nb1.cells = [

nbf.v4.new_markdown_cell("""# 📡 Notebook 1 — Data Collection
## VALORANT Creator Program | Q3 + Q4 2024

**Purpose:** Pull live creator performance data from the YouTube Data API v3,
cache it to CSV, and document every step for full reproducibility.

**Data Sources:**
- Primary: YouTube Data API v3 (channel stats + video-level metrics)
- Secondary: Google Trends via `pytrends` (run `fetch_trends.py` separately)

**How to refresh data:** Set `REFRESH_DATA = True` in the cell below and re-run all cells.
This re-calls the YouTube API and overwrites the cached CSVs.
If `REFRESH_DATA = False`, the notebook loads from existing CSVs (no API quota used).

---
### 🔁 How to Reproduce This Manually
1. Get a free YouTube Data API v3 key: [console.cloud.google.com](https://console.cloud.google.com)
   → Create Project → Enable "YouTube Data API v3" → Credentials → Create API Key
2. Set your key in the `API_KEY` variable below
3. Set `REFRESH_DATA = True`
4. Run all cells — data is saved to `data/raw/`

**Quota cost per full refresh:** ~800 units / 10,000 daily free limit
"""),

nbf.v4.new_code_cell("""# ─── CONFIGURATION — edit these ──────────────────────────────────────────────
REFRESH_DATA = False        # Set True to re-call the YouTube API
API_KEY      = "YOUR_API_KEY_HERE"   # Paste your YouTube Data API v3 key

# Campaign period
Q4_START = "2024-10-01T00:00:00Z"
Q4_END   = "2024-12-31T23:59:59Z"
Q3_START = "2024-07-01T00:00:00Z"
Q3_END   = "2024-09-30T23:59:59Z"

# Creators in the program — channel IDs verified via YouTube API
CREATORS = {
    "TenZ":            {"channel_id": "UCckPYr9b_iVucz8ID1Q67sw", "tier": "Macro"},
    "tarik":           {"channel_id": "UCTbtlMEiBfs0zZLQyJzR0Uw", "tier": "Macro"},
    "Kyedae":          {"channel_id": "UCxjdy5n9BxX_6RTL8Dt_7pg", "tier": "Macro"},
    "aceu":            {"channel_id": "UCBugd2yQNL4TNwHdA56GdnA", "tier": "Macro"},
    "Sinatraa":        {"channel_id": "UCABUGfcFJhffRFZxSl-mIiw", "tier": "Mid-Tier"},
    "Protatomonster":  {"channel_id": "UCdlvbGGgwfF97wlH7rC8Qng", "tier": "Mid-Tier"},
}

# Data paths
import os
RAW_DIR     = os.path.join(os.path.dirname(os.getcwd()), "data", "raw")   if "notebooks" in os.getcwd() else "data/raw"
MODELED_DIR = os.path.join(os.path.dirname(os.getcwd()), "data", "modeled") if "notebooks" in os.getcwd() else "data/modeled"
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(MODELED_DIR, exist_ok=True)

print(f"REFRESH_DATA = {REFRESH_DATA}")
print(f"Raw data dir : {RAW_DIR}")
"""),

nbf.v4.new_markdown_cell("""---
## Step 1 — Install Dependencies
"""),

nbf.v4.new_code_cell("""import subprocess, sys

def install(pkg):
    subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"])

for pkg in ["google-api-python-client", "pandas", "pytrends"]:
    try:
        __import__(pkg.replace("-", "_").split("_python")[0])
    except ImportError:
        print(f"Installing {pkg}...")
        install(pkg)

import pandas as pd
from googleapiclient.discovery import build
from datetime import datetime

print("All dependencies ready ✓")
"""),

nbf.v4.new_markdown_cell("""---
## Step 2 — YouTube API: Channel Statistics

**API Endpoint:** `GET /youtube/v3/channels`
**Parts fetched:** `snippet, statistics`
**What we get:** subscriber count, lifetime views, video count per channel
**Quota cost:** 1 unit per channel = 6 units total
"""),

nbf.v4.new_code_cell("""CHANNEL_CSV = f"{RAW_DIR}/channel_stats.csv"

def fetch_channel_stats(api_key, creator_map):
    \"\"\"Fetch channel-level statistics for all creators.\"\"\"
    youtube = build("youtube", "v3", developerKey=api_key)
    ids = [v["channel_id"] for v in creator_map.values()]

    response = youtube.channels().list(
        part="snippet,statistics",
        id=",".join(ids)
    ).execute()

    records = []
    for item in response["items"]:
        creator = next((k for k,v in creator_map.items() if v["channel_id"] == item["id"]), item["id"])
        records.append({
            "creator":       creator,
            "channel_id":    item["id"],
            "tier":          creator_map.get(creator, {}).get("tier", "Unknown"),
            "subscribers":   int(item["statistics"].get("subscriberCount", 0)),
            "lifetime_views":int(item["statistics"].get("viewCount", 0)),
            "video_count":   int(item["statistics"].get("videoCount", 0)),
            "country":       item["snippet"].get("country", "N/A"),
        })
    return pd.DataFrame(records)

if REFRESH_DATA:
    print("Fetching channel stats from YouTube API...")
    df_channels = fetch_channel_stats(API_KEY, CREATORS)
    df_channels.to_csv(CHANNEL_CSV, index=False)
    print(f"Saved to {CHANNEL_CSV}")
else:
    df_channels = pd.read_csv(CHANNEL_CSV)
    print(f"Loaded from cache: {CHANNEL_CSV}")

print(f"\\n{len(df_channels)} channels loaded")
df_channels[["creator","tier","subscribers","lifetime_views","video_count"]]
"""),

nbf.v4.new_markdown_cell("""---
## Step 3 — YouTube API: Video IDs for Q3 & Q4 2024

**API Endpoint:** `GET /youtube/v3/search`
**Filter:** `type=video`, `publishedAfter/Before` for date range
**Quota cost:** ~100 units per creator × 6 creators × 2 quarters = ~1,200 units

> **Note on the 20-result cap:** The search endpoint caps at 50 results per page.
> We sample the 10 most recent videos per creator per quarter.
> In a production pipeline, you'd paginate with `pageToken` to get all videos.
"""),

nbf.v4.new_code_cell("""def fetch_video_ids(youtube, channel_id, after, before, max_results=20):
    \"\"\"Return list of video IDs published in a date window.\"\"\"
    response = youtube.search().list(
        part="id",
        channelId=channel_id,
        type="video",
        order="date",
        publishedAfter=after,
        publishedBefore=before,
        maxResults=max_results
    ).execute()
    return [item["id"]["videoId"] for item in response.get("items", []) if "videoId" in item["id"]]


def fetch_video_stats(youtube, video_ids):
    \"\"\"Fetch statistics + metadata for a list of video IDs (max 50 per call).\"\"\"
    if not video_ids:
        return []
    response = youtube.videos().list(
        part="statistics,snippet,contentDetails",
        id=",".join(video_ids[:50])
    ).execute()

    records = []
    for v in response.get("items", []):
        stats = v["statistics"]
        records.append({
            "video_id":       v["id"],
            "title":          v["snippet"]["title"],
            "published_date": v["snippet"]["publishedAt"][:10],
            "month":          v["snippet"]["publishedAt"][:7],
            "views":          int(stats.get("viewCount", 0)),
            "likes":          int(stats.get("likeCount", 0)),
            "comments":       int(stats.get("commentCount", 0)),
            "duration":       v["contentDetails"]["duration"],
        })
    return records

print("Helper functions defined ✓")
"""),

nbf.v4.new_code_cell("""import time

Q4_CSV = f"{RAW_DIR}/q4_2024_videos.csv"
Q3_CSV = f"{RAW_DIR}/q3_2024_videos.csv"

def build_video_dataframe(api_key, creator_map, after, before, label):
    \"\"\"Fetch all videos for all creators in a given quarter.\"\"\"
    youtube = build("youtube", "v3", developerKey=api_key)
    all_rows = []

    for creator, meta in creator_map.items():
        print(f"  Fetching {label} videos for {creator}...", end=" ")
        ids = fetch_video_ids(youtube, meta["channel_id"], after, before)
        rows = fetch_video_stats(youtube, ids[:10])  # sample top 10

        for r in rows:
            r["creator"]     = creator
            r["subscribers"] = df_channels.loc[df_channels["creator"]==creator, "subscribers"].values[0]
            r["tier"]        = meta["tier"]
            r["engagements"] = r["likes"] + r["comments"]
            r["engagement_rate"] = round(r["engagements"] / max(r["views"], 1) * 100, 4)

        all_rows.extend(rows)
        print(f"{len(rows)} videos")
        time.sleep(0.5)   # gentle rate limiting

    return pd.DataFrame(all_rows)

if REFRESH_DATA:
    print("Fetching Q4 2024 videos...")
    df_q4 = build_video_dataframe(API_KEY, CREATORS, Q4_START, Q4_END, "Q4")
    df_q4.to_csv(Q4_CSV, index=False)
    print(f"\\nQ4 saved: {len(df_q4)} rows → {Q4_CSV}")

    print("\\nFetching Q3 2024 videos...")
    df_q3 = build_video_dataframe(API_KEY, CREATORS, Q3_START, Q3_END, "Q3")
    df_q3.to_csv(Q3_CSV, index=False)
    print(f"Q3 saved: {len(df_q3)} rows → {Q3_CSV}")
else:
    df_q4 = pd.read_csv(Q4_CSV)
    df_q3 = pd.read_csv(Q3_CSV)
    print(f"Loaded from cache — Q4: {len(df_q4)} rows | Q3: {len(df_q3)} rows")

print("\\nQ4 sample:")
df_q4.head(3)[["creator","title","published_date","views","likes","comments","engagement_rate"]]
"""),

nbf.v4.new_markdown_cell("""---
## Step 4 — Google Trends: Search Interest (Consideration Proxy)

**Source:** Google Trends via `pytrends`
**Search term:** "valorant" | US | Weekly | Jul 1 – Dec 31, 2024
**What it measures:** Relative search interest (0–100 scale, 100 = peak week)
**Why this matters:** Search interest = downstream intent signal — when people search
"valorant" more, it reflects brand consideration and potential player acquisition.

**How to run manually:**
```
python fetch_trends.py
```
Or visit [trends.google.com](https://trends.google.com) → search "valorant" → US →
July–December 2024 → download CSV.

> This data is pre-cached in `data/raw/search_interest_monthly.csv`.
> Run `fetch_trends.py` to refresh it with live data.
"""),

nbf.v4.new_code_cell("""TRENDS_MONTHLY_CSV = f"{RAW_DIR}/search_interest_monthly.csv"

try:
    df_trends = pd.read_csv(TRENDS_MONTHLY_CSV)
    print(f"Google Trends loaded: {len(df_trends)} months")
    print(df_trends.to_string(index=False))
except FileNotFoundError:
    print("⚠️  Google Trends data not found.")
    print("Run: python fetch_trends.py")
    print("Creating placeholder so notebook continues...")
    df_trends = pd.DataFrame({
        "month": ["2024-07","2024-08","2024-09","2024-10","2024-11","2024-12"],
        "avg_search_interest": [None]*6
    })
    print("\\nPlaceholder created — refresh with fetch_trends.py for real values.")
"""),

nbf.v4.new_markdown_cell("""---
## Step 5 — Data Summary & Validation
"""),

nbf.v4.new_code_cell("""print("=" * 60)
print("DATA COLLECTION SUMMARY")
print("=" * 60)
print(f"Channels loaded    : {len(df_channels)}")
print(f"Q4 videos loaded   : {len(df_q4)}")
print(f"Q3 videos loaded   : {len(df_q3)}")
print(f"Trends months      : {len(df_trends)}")
print()

print("Q4 2024 — Videos per creator:")
print(df_q4.groupby("creator")["video_id"].count().reset_index().rename(columns={"video_id":"videos"}).to_string(index=False))
print()

print("Q3 2024 — Videos per creator:")
print(df_q3.groupby("creator")["video_id"].count().reset_index().rename(columns={"video_id":"videos"}).to_string(index=False))
print()

# Check for missing values
issues = []
for df, name in [(df_q4, "Q4"), (df_q3, "Q3")]:
    nulls = df[["views","likes","comments"]].isnull().sum().sum()
    zeros = (df["views"] == 0).sum()
    if nulls: issues.append(f"{name}: {nulls} null values in metrics")
    if zeros: issues.append(f"{name}: {zeros} videos with 0 views (may be age-restricted)")

if issues:
    print("⚠️  Data quality issues:")
    for i in issues: print(f"   - {i}")
else:
    print("✅  No data quality issues found.")

print()
print("All data ready for Notebook 2 → Measurement Framework")
"""),

nbf.v4.new_markdown_cell("""---
## Data Collection Limitations (Documented for Assessment)

| Limitation | Impact | Mitigation |
|---|---|---|
| Max 10 videos sampled per creator per quarter | May miss outliers | Paginate with `pageToken` in production |
| Views accumulate post-publish | Dec videos have fewer days to accumulate | Normalize by days-since-publish in Notebook 2 |
| No impression data (requires channel OAuth) | Can't compute true reach | Use views as awareness proxy |
| No CTR data from YouTube Studio | Can't track click-to-site | Use ER and search lift as intent proxies |
| Spend data not public | Can't compute real CPE | Model from industry benchmarks (documented) |
| Google Trends requires separate run | Search interest may be stale | Run `fetch_trends.py` before analysis |
"""),
]

nb1_path = "01_data_collection.ipynb"
with open(nb1_path, "w") as f:
    nbf.write(nb1, f)
print(f"✅ Notebook 1 written: {nb1_path}")
print(f"   Cells: {len(nb1.cells)}")
