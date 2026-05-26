import streamlit as st
import numpy as np
import pandas as pd
import datetime
import urllib.request
import json

# Setup
st.set_page_config(page_title="SOFI Mobile Command Engine", layout="centered")

# --- UI STYLES ---
st.markdown("""
<style>
.metric-card { background-color: #ffffff; padding: 12px; border-radius: 8px; border: 2px solid #cbd5e0; color: #000 !important; margin-bottom: 10px; }
.metric-card-floor { background-color: #0c2310; padding: 12px; border-radius: 8px; border: 2px solid #2ecc71; color: #fff !important; margin-bottom: 10px; }
.badge-fair { background-color: #2ecc71; color: #fff !important; padding: 6px 12px; border-radius: 4px; font-weight: bold; }
.badge-trapdoor { background-color: #ff9f43; color: #fff !important; padding: 6px 12px; border-radius: 4px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.title("🦅 SOFI Mobile Command Engine")

# --- DATA FETCHING ---
@st.cache_data(ttl=600)
def fetch_live_price():
    # Using Yahoo Finance API endpoint
    url = "https://query1.finance.yahoo.com/v8/finance/chart/SOFI?range=1d&interval=1d"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as response:
        data = json.loads(response.read().decode())
        return round(data['chart']['result'][0]['meta']['regularMarketPrice'], 2)

if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

spot_price = fetch_live_price()

# --- Q1 2026 FUNDAMENTAL CALCULATION ---
# Baselines as of March 31, 2026
q1_date = datetime.date(2026, 3, 31)
today_date = datetime.date.today()
days_elapsed = max((today_date - q1_date).days, 0)

# Growth Velocities
member_velocity = 12175 # Q1 additions / 90 days
tbvps_velocity = 0.00788 # (TBV growth / total shares) / 90 days
prod_velocity = 20000 # Q1 additions / 90 days

curr_members = 14.70 + ((days_elapsed * member_velocity) / 1_000_000)
curr_tbvps = 7.21 + (days_elapsed * tbvps_velocity)
curr_prods = 22.20 + ((days_elapsed * prod_velocity) / 1_000_000)

# URFP Model
urfp = np.mean([
    curr_members * 1.00,
    curr_tbvps * 2.00,
    (curr_tbvps * 1.5) + 4.60,
    (curr_prods * 750) / 1000 # Normalized Cross-Sell Proxy
])

# --- DISPLAY ---
st.markdown(f"<div class='metric-card'><b>📊 Spot:</b> ${spot_price:.2f}</div>", unsafe_allow_html=True)
st.markdown(f"<div class='metric-card-floor'><b>🛡️ URFP:</b> ${urfp:.2f}</div>", unsafe_allow_html=True)

# --- BACKTESTED STRATEGY ENGINE ---
HISTORICAL_SIGMA = 0.038
horizons = [
    {"week": 1, "date_str": "May 29", "dte": 4, "max_pain": 16.00},
    {"week": 2, "date_str": "Jun 05", "dte": 11, "max_pain": 16.50}
]

for h in horizons:
    mp = h["max_pain"]
    dev = abs(spot_price - mp) / spot_price
    
    if dev <= HISTORICAL_SIGMA:
        badge = "<span class='badge-fair'>🟢 PINNING</span>"
        action = "Neutral: Statistically Pinned."
    elif mp < (urfp * (1 - HISTORICAL_SIGMA)):
        badge = "<span class='badge-trapdoor'>🚨 TRAPDOOR</span>"
        action = f"Sell Puts at ${mp:.2f}"
    else:
        badge = "⚪ FAIR VALUE"
        action = "Hold core positions."
        
    st.markdown(f"**Week {h['week']} ({h['date_str']})**: {badge} - {action}")
