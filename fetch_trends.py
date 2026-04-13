
# fetch_trends.py - Pull real Google Trends data for the Valorant Q3/Q4 2024 analysis.
#
# HOW TO RUN:
#   python.exe fetch_trends.py   (from the hardscope-assessment folder)
#
# MANUAL REPLICATION (without code):
#   1. Go to https://trends.google.com/trends/explore
#   2. Search term: valorant | Location: United States
#   3. Time range: 7/1/2024 to 12/31/2024
#   4. Click the download arrow on the "Interest over time" chart
#   5. Save as search_interest.csv inside data/raw/

# ── Compatibility patch: pytrends 4.9.x + urllib3 2.x ────────────────────────
import urllib3.util.retry as _retry_module
_orig_retry_init = _retry_module.Retry.__init__
def _patched_retry_init(self, *args, **kwargs):
    if 'method_whitelist' in kwargs:
        kwargs['allowed_methods'] = kwargs.pop('method_whitelist')
    _orig_retry_init(self, *args, **kwargs)
_retry_module.Retry.__init__ = _patched_retry_init
# ─────────────────────────────────────────────────────────────────────────────

import pandas as pd
from pytrends.request import TrendReq

print("Connecting to Google Trends...")

pt = TrendReq(hl='en-US', tz=360, timeout=(10, 30), retries=3, backoff_factor=0.5)

pt.build_payload(
    kw_list=['valorant'],
    cat=0,
    timeframe='2024-07-01 2024-12-31',
    geo='US',
    gprop=''
)

print("Fetching interest over time...")
df = pt.interest_over_time()

if df.empty:
    print("No data returned. Google may be rate-limiting. Wait 2 minutes and try again.")
else:
    df = df.reset_index()
    df = df.rename(columns={'date': 'week', 'valorant': 'valorant_search_interest'})
    df = df[['week', 'valorant_search_interest']]
    df['week'] = df['week'].dt.strftime('%Y-%m-%d')
    df['month'] = df['week'].str[:7]

    df.to_csv('data/raw/search_interest.csv', index=False)
    print(f"\nSaved {len(df)} weeks of data to data/raw/search_interest.csv")
    print("\nPreview:")
    print(df.to_string(index=False))

    monthly = df.groupby('month')['valorant_search_interest'].mean().round(1).reset_index()
    monthly.columns = ['month', 'avg_search_interest']
    monthly.to_csv('data/raw/search_interest_monthly.csv', index=False)
    print(f"\nMonthly averages saved to data/raw/search_interest_monthly.csv")
    print(monthly.to_string(index=False))

print("\nDone. You can now run the notebooks.")
