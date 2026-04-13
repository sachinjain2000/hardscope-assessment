"""
run_pipeline.py - Standalone measurement pipeline for HardScope assessment.

Run from project root:
    python run_pipeline.py

Generates:
    data/modeled/creator_campaign_metrics.csv
    data/modeled/flagging_alerts.csv
    data/modeled/incrementality_q3_q4.csv
"""

import os
import re
import pandas as pd
import numpy as np
from datetime import date

ANALYSIS_DATE = date(2025, 1, 15)
Q3_MONTHS = ['2024-07', '2024-08', '2024-09']
Q4_MONTHS = ['2024-10', '2024-11', '2024-12']

# ── Modelled monthly spend (IMH 2024 benchmarks — not actual rates) ─────────
# Replace with real contract figures once available. All CPE outputs are
# labelled "modelled" throughout. See METHODOLOGY.md Limitation 2.
MONTHLY_SPEND = {
    'TenZ':           25000,
    'tarik':          20000,
    'Kyedae':         22000,
    'aceu':           28000,
    'Sinatraa':        8000,
    'Protatomonster':  7000,
}

# ── Global benchmark ─────────────────────────────────────────────────────────
ER_BENCHMARK           = 3.87   # Statista 2024 gaming YouTube average
CPE_EFFICIENT          = 0.11
CPE_ACCEPTABLE         = 0.25
ER_DECLINING_THRESHOLD = 0.5
ER_LOW_THRESHOLD       = 1.94   # 50% of global benchmark

# ── Tier-adjusted ER benchmarks (Influencer Marketing Hub 2024) ──────────────
# ER scales inversely with audience size. Applying a single global benchmark
# overstates Macro/Mega performance and understates Mid-tier underperformance.
# See METHODOLOGY.md Limitation 3 for full rationale.
TIER_ER_BENCHMARKS = {
    'Mega':  2.0,   # >5M subscribers
    'Macro': 3.0,   # 1M-5M subscribers
    'Mid':   4.5,   # 500K-1M subscribers
    'Micro': 6.0,   # <500K subscribers
}

BASE  = os.path.dirname(os.path.abspath(__file__))
RAW   = os.path.join(BASE, 'data', 'raw')
MODEL = os.path.join(BASE, 'data', 'modeled')
os.makedirs(MODEL, exist_ok=True)

print("Loading raw data...")
q3 = pd.read_csv(os.path.join(RAW, 'q3_2024_videos.csv'))
q4 = pd.read_csv(os.path.join(RAW, 'q4_2024_videos.csv'))
channel_stats = pd.read_csv(os.path.join(BASE, 'data', 'channel_stats.csv'))
trends = pd.read_csv(os.path.join(RAW, 'search_interest_monthly.csv'))

videos = pd.concat([q3, q4], ignore_index=True)
videos['published_date'] = pd.to_datetime(videos['published_date'])
print(f"  Loaded {len(videos)} videos ({len(q3)} Q3 + {len(q4)} Q4)")

def parse_duration_seconds(iso_str):
    if pd.isna(iso_str): return 0
    h = int(re.search(r'(\d+)H', iso_str).group(1)) if re.search(r'(\d+)H', iso_str) else 0
    m = int(re.search(r'(\d+)M', iso_str).group(1)) if re.search(r'(\d+)M', iso_str) else 0
    s = int(re.search(r'(\d+)S', iso_str).group(1)) if re.search(r'(\d+)S', iso_str) else 0
    return h * 3600 + m * 60 + s

def classify_content_type(seconds):
    minutes = seconds / 60
    if minutes < 2: return 'Short'
    elif minutes <= 20: return 'Mid-form'
    else: return 'Long-form'

videos['duration_seconds'] = videos['duration'].apply(parse_duration_seconds)
videos['content_type']     = videos['duration_seconds'].apply(classify_content_type)

videos['days_since_publish'] = (
    pd.Timestamp(ANALYSIS_DATE) - videos['published_date']
).dt.days.clip(lower=1)
videos['views_per_day'] = (videos['views'] / videos['days_since_publish']).round(1)

ch = channel_stats[['creator', 'subscribers', 'tier']].copy()
videos = videos.drop(columns=['subscribers'], errors='ignore')
videos = videos.merge(ch, on='creator', how='left')

videos['quality_engagement_index'] = ((videos['likes'] + videos['comments'] * 3) / videos['views'] * 100).round(4)
videos['reach_index'] = (videos['views'] * (1 + videos['engagement_rate'] / 100)).round(0).astype(int)
videos['watch_time_hrs'] = (videos['views'] * videos['duration_seconds'] * 0.5 / 3600).round(1)

# Flag TenZ Q3 viral outlier (7.4M views, PT56S Short) — excluded from ER baseline
# to prevent inflating Q3 ER to 4.51% (normalized: 3.58%). Raw data preserved.
videos['is_viral_outlier'] = (
    (videos['creator'] == 'TenZ') & (videos['month'].isin(Q3_MONTHS)) & (videos['views'] > 5_000_000)
)

print("Aggregating to monthly level...")

def aggregate_to_monthly(df):
    agg = df.groupby(['creator', 'month', 'tier']).agg(
        total_views=('views','sum'), total_likes=('likes','sum'),
        total_comments=('comments','sum'), total_engagements=('engagements','sum'),
        video_count=('video_id','count'), avg_views_per_day=('views_per_day','mean'),
        avg_duration_sec=('duration_seconds','mean'), total_watch_hrs=('watch_time_hrs','sum'),
        subscribers=('subscribers','first'),
    ).reset_index()
    agg['engagement_rate'] = (agg['total_engagements'] / agg['total_views'] * 100).round(4)
    agg['quality_engagement_index'] = ((agg['total_likes'] + agg['total_comments'] * 3) / agg['total_views'] * 100).round(4)
    agg['reach_index'] = (agg['total_views'] * (1 + agg['engagement_rate'] / 100)).round(0).astype(int)

    # Spend & CPE (modelled — see MONTHLY_SPEND note above)
    agg['est_monthly_spend'] = agg['creator'].map(MONTHLY_SPEND)
    agg['cpe'] = (agg['est_monthly_spend'] / agg['total_engagements']).round(4)
    agg['cpe_tier'] = pd.cut(agg['cpe'], bins=[0, CPE_EFFICIENT, CPE_ACCEPTABLE, float('inf')],
                              labels=['Efficient', 'Acceptable', 'Review'])

    # Tier-adjusted ER benchmark — more precise than single global benchmark
    agg['tier_er_benchmark'] = agg['tier'].map(TIER_ER_BENCHMARKS).fillna(ER_BENCHMARK)
    # How creator ER compares to their own tier benchmark (>1.0 = above, <1.0 = below)
    agg['er_vs_tier_benchmark'] = (agg['engagement_rate'] / agg['tier_er_benchmark']).round(3)

    agg['avg_views_per_day'] = agg['avg_views_per_day'].round(1)
    agg['avg_duration_sec'] = agg['avg_duration_sec'].round(0).astype(int)
    agg['total_watch_hrs'] = agg['total_watch_hrs'].round(1)
    return agg

monthly = aggregate_to_monthly(videos)

trends.columns = ['month', 'avg_search_interest']
monthly = monthly.merge(trends, on='month', how='left')
monthly['avg_search_interest'] = monthly['avg_search_interest'].round(1)

print("Computing incrementality (period-over-period proxy — not causal lift)...")
# Note: delta_er_pp = Q4 avg ER - Q3 normalized avg ER.
# This measures relative performance change, not causal incrementality.
# True incrementality requires a holdout study. See METHODOLOGY.md Limitation 1.

videos_q3_norm = videos[videos['month'].isin(Q3_MONTHS)].copy()
videos_q3_norm = videos_q3_norm[~videos_q3_norm['is_viral_outlier']]

q3_norm_agg = videos_q3_norm.groupby('creator').agg(
    q3_total_views=('views','sum'), q3_total_engagements=('engagements','sum'),
    q3_video_ct=('video_id','count'),
).reset_index()
q3_norm_agg['q3_avg_er'] = (q3_norm_agg['q3_total_engagements'] / q3_norm_agg['q3_total_views'] * 100).round(4)
q3_norm_agg['q3_avg_views'] = q3_norm_agg['q3_total_views']
q3_avg = q3_norm_agg[['creator', 'q3_avg_er', 'q3_avg_views', 'q3_video_ct']].copy()

q4_avg = monthly[monthly['month'].isin(Q4_MONTHS)].groupby('creator').agg(
    q4_avg_er=('engagement_rate','mean'), q4_avg_views=('total_views','mean'),
    q4_video_ct=('video_count','sum'),
).round(4).reset_index()

incrementality = q3_avg.merge(q4_avg, on='creator')
incrementality['delta_er_pp'] = (incrementality['q4_avg_er'] - incrementality['q3_avg_er']).round(4)
incrementality['delta_views_pct'] = (
    (incrementality['q4_avg_views'] - incrementality['q3_avg_views']) / incrementality['q3_avg_views'] * 100
).round(1)
incrementality['trend'] = incrementality['delta_er_pp'].apply(
    lambda x: 'Improving' if x > 0.1 else ('Declining' if x < -0.1 else 'Flat')
)
monthly = monthly.merge(incrementality[['creator', 'delta_er_pp', 'trend']], on='creator', how='left')

print("Running alert flags...")
alerts = []
monthly_sorted = monthly.sort_values(['creator', 'month'])
monthly_sorted['er_mom_change'] = monthly_sorted.groupby('creator')['engagement_rate'].diff()

for _, row in monthly_sorted.iterrows():
    creator = row['creator']
    month   = row['month']
    er      = row['engagement_rate']
    cpe     = row['cpe']
    views   = row['total_views']
    mom     = row.get('er_mom_change', None)
    tier_bm = row.get('tier_er_benchmark', ER_BENCHMARK)

    if pd.notna(mom) and mom < -ER_DECLINING_THRESHOLD:
        alerts.append({'creator': creator, 'month': month,
                       'alert_type': 'Declining ER',
                       'detail': f'ER dropped {abs(mom):.2f}pp MoM'})

    if views > 500_000 and er < 2.0:
        alerts.append({'creator': creator, 'month': month,
                       'alert_type': 'High Volume / Low Quality',
                       'detail': f'{views:,.0f} views but ER only {er:.2f}%'})

    if er < ER_LOW_THRESHOLD:
        alerts.append({'creator': creator, 'month': month,
                       'alert_type': 'Below Global Benchmark Floor',
                       'detail': f'ER {er:.2f}% < 50% of global {ER_BENCHMARK}% benchmark'})

    if pd.notna(cpe) and cpe > CPE_ACCEPTABLE:
        alerts.append({'creator': creator, 'month': month,
                       'alert_type': 'CPE Overrun',
                       'detail': f'CPE ${cpe:.2f} (modelled) exceeds ${CPE_ACCEPTABLE} ceiling'})

    # Tier-adjusted alert: flag if ER < 80% of tier benchmark
    if er < tier_bm * 0.8:
        alerts.append({'creator': creator, 'month': month,
                       'alert_type': 'Below Tier Benchmark',
                       'detail': f'ER {er:.2f}% < 80% of {row["tier"]} benchmark {tier_bm:.1f}%'})

alerts_df = pd.DataFrame(alerts)

master_cols = ['creator','month','tier','subscribers','total_views','total_likes','total_comments',
               'total_engagements','video_count','engagement_rate','quality_engagement_index',
               'reach_index','avg_views_per_day','avg_duration_sec','total_watch_hrs',
               'est_monthly_spend','cpe','cpe_tier','tier_er_benchmark','er_vs_tier_benchmark',
               'avg_search_interest','delta_er_pp','trend']
master_cols = [c for c in master_cols if c in monthly.columns]
master = monthly[master_cols].sort_values(['creator', 'month'])

master.to_csv(os.path.join(MODEL, 'creator_campaign_metrics.csv'), index=False)
print(f"  Saved creator_campaign_metrics.csv ({len(master)} rows, {len(master.columns)} cols)")
incrementality.to_csv(os.path.join(MODEL, 'incrementality_q3_q4.csv'), index=False)
print(f"  Saved incrementality_q3_q4.csv ({len(incrementality)} rows)")
if len(alerts_df) > 0:
    alerts_df.to_csv(os.path.join(MODEL, 'flagging_alerts.csv'), index=False)
    print(f"  Saved flagging_alerts.csv ({len(alerts_df)} alerts)")

print("\n============================================================")
print("Q4 2024 PROGRAM SUMMARY")
print("============================================================")
q4_summary = master[master['month'].isin(Q4_MONTHS)]
print(f"  Total Views:       {q4_summary['total_views'].sum():>12,.0f}")
print(f"  Total Engagements: {q4_summary['total_engagements'].sum():>12,.0f}")
print(f"  Blended ER:        {(q4_summary['total_engagements'].sum() / q4_summary['total_views'].sum() * 100):>11.2f}%")

lb = q4_summary.groupby('creator').agg(
    avg_er=('engagement_rate','mean'),
    tier=('tier','first'),
    tier_bm=('tier_er_benchmark','first'),
).reset_index().sort_values('avg_er', ascending=False)

print("\nQ4 CREATOR LEADERBOARD (with tier-adjusted benchmarks):")
print(f"  {'Creator':<20} {'Q4 ER':>7}  {'Tier':<8}  {'Tier BM':>8}  {'vs Tier BM':>12}")
print("  " + "-"*62)
for _, row in lb.iterrows():
    vs = row['avg_er'] / row['tier_bm']
    flag = '✓ ABOVE' if vs >= 1.0 else ('⚠ BELOW' if vs >= 0.8 else '✗ FAR BELOW')
    print(f"  {row['creator']:<20} {row['avg_er']:>6.2f}%  {row['tier']:<8}  {row['tier_bm']:>7.1f}%  {flag}")

print("\n  NOTE: CPE based on modelled spend — see METHODOLOGY.md Limitation 2")
print("  NOTE: delta_er_pp is period-over-period proxy — not causal lift")
print("\n  Pipeline complete. Outputs in data/modeled/")
