import streamlit as st
import numpy as np
import datetime

# --- CONFIG ---
st.set_page_config(page_title="SOFI Mobile Command Engine", layout="centered")

# --- PARAMETERS ---
# Q1 2026 Baseline (March 31, 2026)
q1_date = datetime.date(2026, 3, 31)
days_elapsed = max((datetime.date.today() - q1_date).days, 0)

# Daily Accretion Calculation
daily_member_add = 0.011593  # Millions
daily_prod_add = 0.019780    # Millions
daily_tbvps_add = 0.0075     # Dollars

curr_m = 14.70 + (days_elapsed * daily_member_add)
curr_p = 22.20 + (days_elapsed * daily_prod_add)
curr_t = 7.21 + (days_elapsed * daily_tbvps_add)

# URFP Calculation (4 Metrics)
metric_1 = curr_m * 1.00                # Member Proxy
metric_2 = curr_t * 2.00                # Tangible Floor
metric_3 = (curr_t * 1.6) + 4.50        # SOTP Price
metric_4 = (curr_p * 720) / 1000        # Cross-Sell Proxy

urfp = np.mean([metric_1, metric_2, metric_3, metric_4])

# --- UI ---
st.title("🦅 SOFI Command Engine")
st.metric("Current URFP", f"${urfp:.2f}")

st.write("### Metric Breakdown")
st.table({
    "Metric": ["Member Proxy", "Tangible Floor", "SOTP Price", "Cross-Sell"],
    "Value": [f"${metric_1:.2f}", f"${metric_2:.2f}", f"${metric_3:.2f}", f"${metric_4:.2f}"]
})

st.info(f"Days since Q1 close: {days_elapsed}")
