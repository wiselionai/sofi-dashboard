import streamlit as st
import numpy as np
import pandas as pd
import datetime
import urllib.request
import json

st.set_page_config(page_title="SOFI Live Multi-Week Options", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@keyframes flash-forest { 0%, 100% { background-color: #0c2310; color: #2ecc71; border: 2px solid #2ecc71; } 50% { background-color: #113f19; color: #fff; border: 2px solid #fff; } }
@keyframes flash-emerald { 0%, 100% { background-color: #1abc9c; color: #ffffff; border: 2px solid #16a085; } 50% { background-color: #2ecc71; color: #ffffff; border: 2px solid #fff; } }
@keyframes flash-red { 0%, 100% { background-color: #2b1011; color: #e74c3c; border: 2px solid #e74c3c; } 50% { background-color: #bd2130; color: #fff; border: 2px solid #fff; } }
.flash-signal-put-sell { padding: 15px; border-radius: 8px; font-size: 18px; font-weight: bold; text-align: center; animation: flash-forest 2s infinite; }
.flash-signal-accumulate { padding: 15px; border-radius: 8px; font-size: 18px; font-weight: bold; text-align: center; animation: flash-emerald 1.5s infinite; }
.flash-signal-sell { padding: 15px; border-radius: 8px; font-size: 18px; font-weight: bold; text-align: center; animation: flash-red 2s infinite; }
.normal-signal { padding: 15px; border-radius: 8px; font-size: 18px; font-weight: bold; text-align: center; background-color: #1e242b; color: #fff; border: 1px solid #34495e; }
</style>
""", unsafe_allow_html=True)

st.title("⚡ SOFI Live Multi-Week Options Workstation")
st.caption("100% Autonomous Forward-Curve Option Scraping & Accretion Analytics")

# ================= SECURE DATA FETCH ENGINE =================
@st.cache_data(ttl=60)
def fetch_live_market_data():
    spot_price = 15.66
    today = datetime.date.today()
    exp_dates = []
    
    # 1. Fetch Real-Time Spot Equity Price
    try:
        url = "https://yahoo.com"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            meta = data['chart']['result']['meta']
            spot_price = round(meta['regularMarketPrice'], 2)
    except:
        pass
        
    # 2. Fetch Option Expiration Chain Calendar Loop
    try:
        opt_url = "https://yahoo.com"
        req_opt = urllib.request.Request(opt_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req_opt, timeout=10) as response:
            opt_data = json.loads(response.read().decode())
            res = opt_data['optionChain']['result'][0]
            timestamps = res['expirationDates']
            if timestamps:
                # Store the upcoming 4 valid future expirations
                future_dates = [datetime.datetime.fromtimestamp(ts).date() for ts in timestamps if ts >= datetime.datetime.combine(today, datetime.time.min).timestamp()]
                exp_dates = future_dates[:4]
    except:
        pass

    # Default fallback generation if exchange feeds time out
    if len(exp_dates) < 4:
        days_until_friday = (4 - today.weekday()) % 7
        if days_until_friday == 0: days_until_friday = 7
        exp_dates = [today + datetime.timedelta(days=days_until_friday + (i * 7)) for i in range(4)]
        
    # 3. Pull Multi-Horizon Implied Volatilities and Premiums
    horizon_data = []
    for i, target_date in enumerate(exp_dates):
        dte = max((target_date - today).days, 0)
        iv_val = 0.45
        last_price = 0.15
        
        try:
            opt_url = f"https://yahoo.com?date={int(datetime.datetime.combine(target_date, datetime.time.min).timestamp())}"
            req_opt = urllib.request.Request(opt_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req_opt, timeout=10) as response:
                opt_data = json.loads(response.read().decode())
                res = opt_data['optionChain']['result'][0]
                options_block = res['options'][0]
                puts = options_block['puts']
                if puts:
                    target_strike = np.floor(spot_price * 2)/2
                    matching_put = min(puts, key=lambda x: abs(x['strike'] - target_strike))
                    last_price = round(matching_put['lastPrice'], 2)
                    iv_val = round(matching_put['impliedVolatility'], 3)
        except:
            pass
            
        horizon_data.append({"week": i+1, "date": target_date, "dte": dte, "iv": iv_val, "premium": last_price})
        
    return spot_price, horizon_data

with st.spinner("Extracting multi-week options structural data curves..."):
    spot_price, horizons = fetch_live_market_data()

# ================= AUTOMATED REAL-TIME FUNDAMENTAL ENGINE =================
q1_date = datetime.date(2026, 3, 31)
today_date = datetime.date.today()
days_elapsed = max((today_date - q1_date).days, 0)

q1_members_baseline = 14.70
daily_member_velocity = 11722
estimated_current_members = q1_members_baseline + ((days_elapsed * daily_member_velocity) / 1_000_000)

q1_tbvps_baseline = 7.21
daily_tbvps_velocity = 0.24 / 30.44
estimated_current_tbvps = q1_tbvps_baseline + (days_elapsed * daily_tbvps_velocity)

q1_products_baseline = 21.80
daily_product_velocity = 20000
estimated_current_products = q1_products_baseline + ((days_elapsed * daily_product_velocity) / 1_000_000)

member_proxy = estimated_current_members * 1.00
tangible_floor = estimated_current_tbvps * 2.00
sotp_price = (estimated_current_tbvps * 1.5) + 4.60
cross_sell_price = (estimated_current_products * 10.0**6 * 750) / 1.09 * 10**-9
urfp = np.mean([member_proxy, tangible_floor, sotp_price, cross_sell_price])

# ================= MAIN DASHBOARD METRICS DISPLAY =================
col_spot, col_urfp, col_days = st.columns(3)
with col_spot:
    st.metric(label="📊 Live SOFI Spot Price", value=f"${spot_price:.2f}", delta=f"{(spot_price - urfp):.2f} Above Floor")
with col_urfp:
    st.metric(label="🛡️ Unified Rising Floor Price (URFP)", value=f"${urfp:.2f}")
with col_days:
    st.metric(label="📈 Elapsed Accretion Runway", value=f"{days_elapsed} Days", delta=f"{estimated_current_members:.2f}M Est. Members")

# ================= MULTI-WEEK FORWARD CURVE ANALYSIS PANEL =================
st.subheader("🔮 Forward Horizon Opportunity Matrix (1 to 4 Weeks Out)")

matrix_rows = []
for h in horizons:
    # Estimate rolling Max Pain baseline for future weeks
    est_future_max_pain = np.floor(spot_price * 2) / 2
    
    # Calculate Expected Boundary Moves using forward IV components
    time_fraction = max(h["dte"], 0.5) / 365.0
    sd_move = spot_price * h["iv"] * np.sqrt(time_fraction)
    lower_bound = max(urfp * 0.95, spot_price - (sd_move + (spot_price * 0.0112)))
    upper_bound = spot_price + (sd_move + (spot_price * 0.0112))
    
    # Structural Signal Router
    sig_html = '<div class="normal-signal">⚪ HOLD / STEADY</div>'
    if spot_price <= urfp:
        if h["dte"] <= 4:
            sig_html = '<div class="flash-signal-put-sell">🌲 HARVEST PUTS</div>'
        else:
            sig_html = '<div class="flash-signal-accumulate">✨ BUY VALUE</div>'
    elif spot_price >= upper_bound * 0.95:
        sig_html = '<div class="flash-signal-sell">🔴 WRITE CALLS</div>'
        
    matrix_rows.append({
        "Horizon": f"Week {h['week']} Expiration",
        "Target Date": h["date"].strftime("%b %d, %Y"),
        "Days Out (DTE)": h["dte"],
        "Live Implied Vol (IV)": f"{h['iv']*100:.1f}%",
        "Live ATM Premium": f"${h['premium']:.2f}",
        "Expected Safe Range Floor": f"${lower_bound:.2f}",
        "Execution Action Alert": sig_html
    })

# Convert array to clean visual frame
df_matrix = pd.DataFrame(matrix_rows)

# Render Custom CSS Grid for complete iPhone readability without cutoffs
for idx, row in df_matrix.iterrows():
    m_col1, m_col2, m_col3 = st.columns([2, 3, 3])
    with m_col1:
        st.write(f"**{row['Horizon']}**")
        st.caption(f"{row['Target Date']} ({row['Days Out (DTE)']} DTE)")
    with m_col2:
        st.write(f"💵 Premium: **{row['Live ATM Premium']}** | IV: `{row['Live Implied Vol (IV)']}`")
        st.caption(f"Safety Floor Limit: {row['Expected Safe Range Floor']}")
    with m_col3:
        st.markdown(row["Execution Action Alert"], unsafe_allow_html=True)
    st.markdown("---")

with st.expander("📈 View Live Daily Accreted Balance Sheet Projections"):
    st.write(f"**Days elapsed since Q1 reported metrics (March 31, 2026)**: {days_elapsed} days")
    f_col1, f_col2, f_col3 = st.columns(3)
    f_col1.metric("👥 Estimated Members", f"{estimated_current_members:.3f}M", f"+{(days_elapsed * daily_member_velocity):,} since Q1")
    f_col2.metric("💳 Estimated Tangible BVPS", f"${estimated_current_tbvps:.3f}", f"+${(days_elapsed * daily_tbvps_velocity):.3f} since Q1")
    f_col3.metric("📦 Estimated Active Products", f"{estimated_current_products:.3f}M", f"+{(days_elapsed * daily_product_velocity):,} since Q1")
