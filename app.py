import streamlit as st
import numpy as np
import pandas as pd
import datetime
import urllib.request
import json

# Page Configuration for Mobile Scannability
st.set_page_config(page_title="SOFI Live Options Dashboard", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for Flashing Alerts and Position Controls
st.markdown("""
<style>
@keyframes flash-forest { 0%, 100% { background-color: #0c2310; color: #2ecc71; border: 2px solid #2ecc71; } 50% { background-color: #113f19; color: #fff; border: 2px solid #fff; } }
@keyframes flash-emerald { 0%, 100% { background-color: #1abc9c; color: #ffffff; border: 2px solid #16a085; } 50% { background-color: #2ecc71; color: #ffffff; border: 2px solid #fff; } }
@keyframes flash-red { 0%, 100% { background-color: #2b1011; color: #e74c3c; border: 2px solid #e74c3c; } 50% { background-color: #bd2130; color: #fff; border: 2px solid #fff; } }
@keyframes flash-orange { 0%, 100% { background-color: #3d220f; color: #f39c12; border: 2px solid #f39c12; } 50% { background-color: #d35400; color: #fff; border: 2px solid #fff; } }

.flash-signal-put-sell { padding: 20px; border-radius: 10px; font-size: 24px; font-weight: bold; text-align: center; animation: flash-forest 2s infinite; margin-bottom: 20px; }
.flash-signal-accumulate { padding: 20px; border-radius: 10px; font-size: 24px; font-weight: bold; text-align: center; animation: flash-emerald 1.5s infinite; margin-bottom: 20px; }
.flash-signal-sell { padding: 20px; border-radius: 10px; font-size: 24px; font-weight: bold; text-align: center; animation: flash-red 2s infinite; margin-bottom: 20px; }
.flash-signal-bail { padding: 25px; border-radius: 10px; font-size: 26px; font-weight: bold; text-align: center; animation: flash-orange 1.5s infinite; margin-bottom: 20px; border: 3px solid #ff0000; }
.normal-signal { padding: 20px; border-radius: 10px; font-size: 24px; font-weight: bold; text-align: center; background-color: #1e242b; color: #fff; border: 2px solid #34495e; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

st.title("⚡ SOFI Live Options Orchestration Dashboard")
st.caption("Fully Automated Real-Time Scraping & Daily Balance Sheet Accretion Tracking")

# ================= SECURE DATA FETCH ENGINE =================
@st.cache_data(ttl=60) # Re-fetches fresh market data every 60 seconds
def fetch_live_market_data():
    spot_price = 15.66
    iv_val = 0.45
    today = datetime.date.today()
    days_until_friday = (4 - today.weekday()) % 7
    if days_until_friday == 0:
        days_until_friday = 7
    target_date = today + datetime.timedelta(days=days_until_friday)
    
    try:
        url = "https://yahoo.com"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            meta = data['chart']['result']['meta']
            spot_price = round(meta['regularMarketPrice'], 2)
    except:
        pass

    try:
        opt_url = f"https://yahoo.com"
        req_opt = urllib.request.Request(opt_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req_opt, timeout=10) as response:
            opt_data = json.loads(response.read().decode())
            res = opt_data['optionChain']['result'][0]
            timestamps = res['expirationDates']
            if timestamps:
                closest_ts = [ts for ts in timestamps if ts >= datetime.datetime.combine(today, datetime.time.min).timestamp()]
                if closest_ts:
                    target_date = datetime.datetime.fromtimestamp(closest_ts[0]).date()
            
            options_block = res['options'][0]
            calls = options_block['calls']
            if calls:
                closest_call = min(calls, key=lambda x: abs(x['strike'] - spot_price))
                iv_val = round(closest_call['impliedVolatility'], 3)
    except:
        pass

    dte = max((target_date - today).days, 0)
    return spot_price, target_date, dte, iv_val

# Execute API Pull
with st.spinner("Pulling real-time market data from exchange rails..."):
    spot_price, target_friday, dte, iv = fetch_live_market_data()

target_friday_str = target_friday.strftime("%b %d, %Y")

# ================= AUTOMATED REAL-TIME FUNDAMENTAL ENGINE =================
# Benchmarked historical anchors from the officially reported Q1 2026 Earnings Release (As of March 31, 2026)
q1_date = datetime.date(2026, 3, 31)
today_date = datetime.date.today()
days_elapsed = max((today_date - q1_date).days, 0)

# 1. Daily Member Accretion (~11,722 members added per day)
q1_members_baseline = 14.70 # Millions
daily_member_velocity = 11722
estimated_current_members = q1_members_baseline + ((days_elapsed * daily_member_velocity) / 1_000_000)

# 2. Daily Tangible Book Value Accretion (~$0.24 per share per month -> ~$0.00789 per day)
q1_tbvps_baseline = 7.21
daily_tbvps_velocity = 0.24 / 30.44
estimated_current_tbvps = q1_tbvps_baseline + (days_elapsed * daily_tbvps_velocity)

# 3. Daily Product Accretion (~20,000 product cross-buys added per day)
q1_products_baseline = 21.80 # Millions
daily_product_velocity = 20000
estimated_current_products = q1_products_baseline + ((days_elapsed * daily_product_velocity) / 1_000_000)

# 4. Estimated standard BVPS accretion for comparison (~$0.27 per share per month -> ~$0.00887 per day)
q1_bvps_baseline = 8.44
daily_bvps_velocity = 0.27 / 30.44
estimated_current_bvps = q1_bvps_baseline + (days_elapsed * daily_bvps_velocity)

# ================= SIDEBAR INPUTS (MONITORING ONLY) =================
st.sidebar.header("🛡️ Active Position Monitoring")
current_premium_value = st.sidebar.number_input("Current Mid-Price of Short Contracts ($)", value=0.15, step=0.01)
initial_premium_collected = st.sidebar.number_input("Initial Premium Captured At Entry ($)", value=0.50, step=0.05)

# Main Dashboard Control for Max Pain Strike
max_pain = st.number_input("🚨 Set Weekly Max Pain Strike ($)", value=np.floor(spot_price * 2)/2, step=0.50)

# ================= MATHEMATICAL MODEL ENGINE =================
# 1. Calculate the 4-Layer Unified Rising Floor Price (URFP) using live-accreted fundamentals
member_proxy = estimated_current_members * 1.00
tangible_floor = estimated_current_tbvps * 2.00
sotp_price = (estimated_current_tbvps * 1.5) + 4.60
cross_sell_price = (estimated_current_products * 10.0**6 * 750) / 1.09 * 10**-9
urfp = np.mean([member_proxy, tangible_floor, sotp_price, cross_sell_price])

# 2. Calculate Ranges and Boundaries using Automated IV
time_fraction = max(dte, 0.5) / 365.0
standard_deviation_move = spot_price * iv * np.sqrt(time_fraction)
historical_buffer = spot_price * 0.0112
lower_range = max(urfp * 0.95, spot_price - (standard_deviation_move + historical_buffer))
upper_range = spot_price + (standard_deviation_move + historical_buffer)

# 3. Theta Acceleration Engine (Using Automated DTE)
if dte >= 3:
    decay_profile = f"Linear / Slow ({dte} DTE)"
    theta_penalty = 0.20
elif dte == 2:
    decay_profile = f"Accelerating / Moderate ({dte} DTE)"
    theta_penalty = 0.50
else:
    decay_profile = f"Terminal / Extreme Collapse ({dte} DTE)"
    theta_penalty = 0.95

# 4. Position Profit Calculation for Bail Engine
profit_percentage = ((initial_premium_collected - current_premium_value) / initial_premium_collected) * 100

# ================= MAIN DASHBOARD DISPLAY =================
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="📊 Live SOFI Spot Price", value=f"${spot_price:.2f}", delta=f"{(spot_price - urfp):.2f} Above URFP Floor")
with col2:
    st.metric(label="🛡️ Unified Rising Floor Price (URFP)", value=f"${urfp:.2f}")
with col3:
    st.metric(label="⏳ Option Time Decay (Theta)", value=decay_profile, delta=f"-{(theta_penalty*100):.0f}% Premium Velocity")

st.info(f"🔮 **Probability Matrix**: Expected Expiration Range for Friday, **{target_friday_str}**: **${lower_range:.2f}** to **${upper_range:.2f}** (Live Implied Volatility: {iv*100:.1f}%)")

# ================= REAL-TIME FUNDAMENTALS TRACKER DISPLAY =================
with st.expander("📈 View Live Daily Accreted Balance Sheet Projections"):
    st.write(f"**Days elapsed since Q1 reported metrics (March 31, 2026)**: {days_elapsed} days")
    f_col1, f_col2, f_col3 = st.columns(3)
    f_col1.metric("👥 Estimated Members", f"{estimated_current_members:.3f}M", f"+{(days_elapsed * daily_member_velocity):,} since Q1")
    f_col2.metric("💳 Estimated Tangible BVPS", f"${estimated_current_tbvps:.3f}", f"+${(days_elapsed * daily_tbvps_velocity):.3f} since Q1")
    f_col3.metric("📦 Estimated Active Products", f"{estimated_current_products:.3f}M", f"+{(days_elapsed * daily_product_velocity):,} since Q1")

# ================= AUTOMATED BAIL ENGINE =================
st.subheader("⚠️ Emergency & Profit Exit Monitoring")

bail_triggered = False
bail_html = ""
bail_recommendation = ""

if profit_percentage >= 80.0 and dte >= 1:
    bail_triggered = True
    bail_html = '<div class="flash-signal-bail">💥 POSITION EXIT: TAKE PROFIT SIGNAL ACTIVE (80%+ EXTRACTED EARLY)</div>'
    bail_recommendation = f"**Bail Action**: Secure your gains immediately. Your open short options have decayed by {profit_percentage:.1f}%. Buy-to-close the contracts now and free up your margin collateral."
elif spot_price < urfp * 0.97:
    bail_triggered = True
    bail_html = '<div class="flash-signal-bail">🚨 EMERGENCY EXIT: STRUCTURAL FLOOR BREAKDOWN ACTIVE</div>'
    bail_recommendation = f"**Bail Action**: The underlying spot price (${spot_price:.2f}) has breached your 3% structural buffer below the ${urfp:.2f} URFP. Buy-to-close immediately or prepare to roll your contracts out 30 days to avoid unwanted equity assignment."

if bail_triggered:
    st.markdown(bail_html, unsafe_allow_html=True)
    st.warning(bail_recommendation)
else:
