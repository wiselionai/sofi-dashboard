import streamlit as st
import numpy as np
import datetime

# --- CONFIG ---
st.set_page_config(page_title="SOFI Command Engine", layout="centered")
spot_price = 16.08 # Update this via API

# --- FUNDAMENTALS ---
q1_date = datetime.date(2026, 3, 31)
days_elapsed = max((datetime.date.today() - q1_date).days, 0)

# Q1 Daily Accretion
curr_members = 14.70 + ((days_elapsed * 0.0116))
curr_tbvps = 7.21 + (days_elapsed * 0.0075)
curr_prods = 22.20 + ((days_elapsed * 0.0198))

# Recalibrated URFP Model
urfp = np.mean([
    curr_members * 1.00,        # Member Proxy
    curr_tbvps * 2.11,          # Tangible Floor (Corrected Multiplier)
    (curr_tbvps * 1.6) + 4.50,  # SOTP
    (curr_prods * 710) / 1000   # Adjusted Cross-Sell Proxy
])

# --- DISPLAY ---
st.title("🦅 SOFI Command Engine")
st.metric("Spot Price", f"${spot_price:.2f}")
st.metric("Calculated URFP", f"${urfp:.2f}")

# --- 4-WEEK STRATEGY ---
horizons = [
    {"date": "May 29", "mp": 16.00},
    {"date": "Jun 05", "mp": 16.50},
    {"date": "Jun 12", "mp": 16.00},
    {"date": "Jun 18", "mp": 15.00}
]

for h in horizons:
    dev = abs(spot_price - h['mp']) / spot_price
    # 3.8% Statistical Pinning
    if dev <= 0.038:
        status, strat = "🟢 PINNING", "Neutral: Statistically Pinned"
    elif h['mp'] < urfp:
        status, strat = "🚨 TRAPDOOR", f"Sell Puts at ${h['mp']:.2f}"
    else:
        status, strat = "⚪ OVEREXTENDED", "Call Hedge / Reduce Delta"
    st.markdown(f"**{h['date']}**: {status} - {strat}")
