import streamlit as st
import numpy as np
import pandas as pd
import datetime
import yfinance as yf

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
st.caption("Fully Automated Real-Time Scraping & Option Degradation Analytics")

# ================= EXTERNAL API DATA FETCH ENGINE =================
@st.cache_data(ttl=60) # Re-fetches fresh market data every 60 seconds
def fetch_live_market_data():
    ticker = yf.Ticker("SOFI")
    
    # 1. Fetch Live Spot Price
    history = ticker.history(period="1d")
    spot_price = round(history['Close'].iloc[-1], 2) if not history.empty else 15.66
    
    # 2. Extract Options Dates and Find Upcoming Friday
    expirations = ticker.options
    today = datetime.date.today()
    
    if expirations:
        exp_dates = [datetime.datetime.strptime(e, "%Y-%m-%d").date() for e in expirations]
        valid_dates = [d for d in exp_dates if d >= today]
        target_date = valid_dates[0] if valid_dates else today
    else:
        days_until_friday = (4 - today.weekday()) % 7
        target_date = today + datetime.timedelta(days=days_until_friday)

    # 3. Calculate Real-Time Days To Expiration (DTE)
    dte = max((target_date - today).days, 0)
    
    # 4. Fetch Implied Volatility (IV) from ATM Option Chain
    try:
        opt_chain = ticker.option_chain(target_date.strftime("%Y-%m-%d"))
        calls = opt_chain.calls
        atm_call = calls.iloc[(calls['strike'] - spot_price).abs().argsort()[:1]]
        iv_val = atm_call['impliedVolatility'].values[0] if not atm_call.empty else 0.45
    except:
        iv_val = 0.45
        
    return spot_price, target_date, dte, iv_val

# Execute API Pull
with st.spinner("Pulling real-time market data from exchange rails..."):
    spot_price, target_friday, dte, iv = fetch_live_market_data()

target_friday_str = target_friday.strftime("%b %d, %Y")

# ================= SIDEBAR INPUTS (BALANCE SHEET ONLY) =================
st.sidebar.header("🛡️ Active Position Monitoring")
current_premium_value = st.sidebar.number_input("Current Mid-Price of Short Contracts ($)", value=0.15, step=0.01)
initial_premium_collected = st.sidebar.number_input("Initial Premium Captured At Entry ($)", value=0.50, step=0.05)

st.sidebar.header("📊 Audited Balance Sheet Inputs")
members = st.sidebar.number_input("Total Registered Members (Millions)", value=15.40, step=0.10)
tbvps = st.sidebar.number_input("Tangible Book Value Per Share ($)", value=7.41, step=0.05)
products = st.sidebar.number_input("Total Products Active (Millions)", value=22.20, step=0.10)

# Main Dashboard Control for Manual Override Option
max_pain = st.number_input("🚨 Override/Set Weekly Max Pain Strike ($)", value=np.floor(spot_price * 2)/2, step=0.50)

# ================= MATHEMATICAL MODEL ENGINE =================
# 1. Calculate the 4-Layer Unified Rising Floor Price (URFP)
member_proxy = members * 1.00
tangible_floor = tbvps * 2.00
sotp_price = (tbvps * 1.5) + 4.60
cross_sell_price = (products * 10.0**6 * 750) / 1.09 * 10**-9
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
    st.success("✅ Position Health: Active positions are inside safe operational parameters. No emergency exit triggers hit.")

# ================= FLASHING TRANSACTION ALERT ENGINE =================
st.subheader("🚨 Real-Time Transaction Alert Execution")

signal_html = ""
trade_recommendation = ""

if not bail_triggered:
    if spot_price <= urfp or max_pain < urfp:
        if theta_penalty >= 0.50:
            target_strike = np.floor(max_pain * 2) / 2
            signal_html = '<div class="flash-signal-put-sell">🌲 TRANSACTION ALERT: ARBITRAGE PUT SELLING WINDOW ACTIVE (DARK FOREST GREEN)</div>'
            trade_recommendation = f"* **Action**: Sell-to-Open (Write) Put Options\\n* **Contract Expiration**: {target_friday_str}\\n* **Strike Price Target**: ${target_strike:.2f}\\n* **Strategic Blueprint**: Write premium directly at the Max Pain support line. Terminal time decay is collapsing extrinsic value above your verified ${urfp:.2f} URFP floor."
        else:
            target_strike = np.floor(spot_price * 2) / 2
            signal_html = '<div class="flash-signal-accumulate">✨ TRANSACTION ALERT: VALUE ACCUMULATION WINDOW ACTIVE (BRIGHT EMERALD GREEN)</div>'
            trade_recommendation = f"* **Action**: Buy-to-Open Call Options\\n* **Contract Expiration**: {target_friday_str}\\n* **Strike Price Target**: ${target_strike:.2f}\\n* **Strategic Blueprint**: Accumulate raw equity or buy calls early in the weekly cycle. Theta decay is slow."
            
    elif spot_price >= upper_range * 0.98 or max_pain > urfp * 1.25:
        target_strike = np.ceil(upper_range * 2) / 2
        signal_html = '<div class="flash-signal-sell">🔴 TRANSACTION ALERT: OVEREXTENDED PREMIUM HARVEST WINDOW ACTIVE</div>'
        trade_recommendation = f"* **Action**: Sell-to-Open (Write) Covered Calls\\n* **Contract Expiration**: {target_friday_str}\\n* **Strike Price Target**: ${target_strike:.2f}\\n* **Strategic Blueprint**: Write calls way out-of-the-money against your inventory. Market momentum has outpaced user milestones."
    else:
        signal_html = '<div class="normal-signal">⚪ CORE STABILITY: HOLD AND HARVEST EXISTING PREMIUM</div>'
