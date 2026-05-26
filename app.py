import streamlit as st
import numpy as np
import datetime
import urllib.request
import json

# --- APP CONFIG ---
st.set_page_config(page_title="SOFI Mobile Command Engine", layout="centered")

# --- DATA FETCHING ---
@st.cache_data(ttl=600)
def fetch_live_price():
    try:
        url = "https://query1.finance.yahoo.com/v8/finance/chart/SOFI?range=1d&interval=1d"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            return round(data['chart']['result'][0]['meta']['regularMarketPrice'], 2)
    except:
        return 16.08

spot_price = fetch_live_price()

# --- FIXED GROWTH ENGINE ---
# Q1 2026 Baselines (March 31, 2026)
q1_date = datetime.date(2026, 3, 31)
days_elapsed = max((datetime.date.today() - q1_date).days, 0)

# Daily Accretion Constants (Based on Q1 2026 Earnings)
member_v = 0.011593  # Millions per day
tbvps_v = 0.0075     # Dollars per day
prod_v = 0.019780    # Millions per day

curr_m = 14.70 + (days_elapsed * member_v)
curr_t = 7.21 + (days_elapsed * tbvps_v)
curr_p = 22.20 + (days_elapsed * prod_v)

# URFP Calculation (Fixed Multipliers)
urfp = np.mean([
    curr_m * 1.00,          # Member Proxy
    curr_t * 2.10,          # Tangible Floor
    (curr_t * 1.55) + 4.50, # SOTP
    (curr_p * 0.70)         # Cross-Sell Proxy
])

# --- UI ---
st.title("🦅 SOFI Command Engine")
st.metric("Spot Price", f"${spot_price:.2f}")
st.metric("Calculated URFP", f"${urfp:.2f}")

st.write("---")
st.subheader("🗓️ 4-Week Strategy Matrix")

horizons = [
    {"date": "May 29", "mp": 16.00},
    {"date": "Jun 05", "mp": 16.50},
    {"date": "Jun 12", "mp": 16.00},
    {"date": "Jun 18", "mp": 15.00}
]

for h in horizons:
    dev = abs(spot_price - h['mp']) / spot_price
    if dev <= 0.038:
        status, strat = "🟢 PINNING", f"Statistically Pinned at ${h['mp']:.2f}"
    elif h['mp'] < urfp:
        status, strat = "🚨 TRAPDOOR", f"Sell Puts at ${h['mp']:.2f}"
    else:
        status, strat = "⚪ OVEREXTENDED", "Consider Call Hedge"
    st.markdown(f"**{h['date']}**: {status} <br> *{strat}*", unsafe_allow_html=True)

if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()
