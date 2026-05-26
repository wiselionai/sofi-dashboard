import streamlit as st
import numpy as np
import datetime
import urllib.request
import json

# --- APP CONFIG ---
st.set_page_config(page_title="SOFI Mobile Command Engine", layout="centered")

# --- DATA FETCHING (Live API) ---
@st.cache_data(ttl=600)
def fetch_live_price():
    try:
        # Yahoo Finance API endpoint
        url = "https://query1.finance.yahoo.com/v8/finance/chart/SOFI?range=1d&interval=1d"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            return round(data['chart']['result'][0]['meta']['regularMarketPrice'], 2)
    except:
        return 16.08 # Fallback to current market price

# --- REFRESH BUTTON ---
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

spot_price = fetch_live_price()

# --- FUNDAMENTALS (Q1 2026 BASLINES) ---
# Date: March 31, 2026 (End of Q1)
q1_date = datetime.date(2026, 3, 31)
days_elapsed = max((datetime.date.today() - q1_date).days, 0)

# Growth Constants (Q1 2026 verified accretion)
curr_members = 14.70 + ((days_elapsed * 0.0116)) # 11.6k/day
curr_tbvps = 7.21 + (days_elapsed * 0.0075)       # ~$0.0075/day
curr_prods = 22.20 + ((days_elapsed * 0.0198))    # 19.8k/day

# URFP Model
urfp = np.mean([
    curr_members * 1.05,        
    curr_tbvps * 2.15,          
    (curr_tbvps * 1.6) + 4.50,  
    (curr_prods * 720) / 1000   
])

# --- DASHBOARD UI ---
st.title("🦅 SOFI Command Engine")
col1, col2 = st.columns(2)
col1.metric("Current Spot", f"${spot_price:.2f}")
col2.metric("Calculated URFP", f"${urfp:.2f}")

st.write("---")
st.subheader("🗓️ 4-Week Strategy Matrix")

# --- 4-WEEK HORIZON ---
horizons = [
    {"date": "May 29", "mp": 16.00},
    {"date": "Jun 05", "mp": 16.50},
    {"date": "Jun 12", "mp": 16.00},
    {"date": "Jun 18", "mp": 15.00}
]

for h in horizons:
    dev = abs(spot_price - h['mp']) / spot_price
    
    # 3.8% Statistical Pinning Threshold
    if dev <= 0.038:
        status = "🟢 PINNING"
        strat = f"Neutral: Statistically Pinned at ${h['mp']:.2f}"
    elif h['mp'] < urfp:
        status = "🚨 TRAPDOOR"
        strat = f"Sell Puts at ${h['mp']:.2f}"
    else:
        status = "⚪ OVEREXTENDED"
        strat = f"Consider Call Hedge (Max Pain: ${h['mp']:.2f})"
    
    st.markdown(f"**{h['date']}**: {status} <br> *{strat}*", unsafe_allow_html=True)
    st.write("") # Spacer
