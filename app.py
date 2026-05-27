import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, date, timedelta

# --- Page Config ---
st.set_page_config(page_title="SOFI Optimizer", layout="centered")
st.title("SOFI TBVPS & Max Pain Optimizer")

# --- 1. TBVPS Logic (Internal Data) ---
@st.cache_data
def get_tbvps_data():
    start_tbvps = 7.68 
    annual_growth = 0.40
    daily_growth_rate = (1 + annual_growth)**(1/365) - 1
    start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    dates = [start_date + timedelta(days=i) for i in range(365)]
    tbvps_values = [start_tbvps * (1 + daily_growth_rate)**i for i in range(365)]
    return pd.DataFrame({'TBVPS': tbvps_values}, index=dates)

df_tbvps = get_tbvps_data()

# --- 2. Max Pain Data ---
# Add your upcoming dates here
max_pain_events = [
    {"date": date(2026, 5, 29), "price": 16.00},
    {"date": date(2026, 6, 5), "price": 16.50},
    {"date": date(2026, 6, 12), "price": 16.00}
]

# --- 3. UI and Data Fetching ---
try:
    ticker = yf.Ticker("SOFI")
    live_price = ticker.history(period="1d")['Close'].iloc[-1]
    
    # Fundamental Metrics
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    if today in df_tbvps.index:
        tbvps_today = df_tbvps.loc[today, 'TBVPS']
        multiple = live_price / tbvps_today
        
        st.subheader("Fundamental Dashboard")
        col1, col2 = st.columns(2)
        col1.metric("SOFI Price", f"${live_price:.2f}")
        col2.metric("TBVPS Multiple", f"{multiple:.2f}x")
        
        if multiple < 2.0:
            st.success("Multiple < 2.0x. Signal: SELL PUTS (Bullish)")
        else:
            st.warning("Multiple > 2.0x. Signal: Market is rich.")
    
    # Max Pain Metrics
    st.subheader("Upcoming Max Pain Event")
    today_date = date.today()
    next_event = next((e for e in max_pain_events if e["date"] >= today_date), None)
    
    if next_event:
        delta = (next_event["date"] - today_date).days
        col3, col4 = st.columns(2)
        col3.metric("Next Max Pain Price", f"${next_event['price']:.2f}")
        col4.metric("Days Until Event", f"{delta} days")
    else:
        st.write("No upcoming events defined.")

except Exception as e:
    st.error(f"Error loading dashboard: {e}")

st.write("---")
st.caption("Optimizer tracks current price vs 40% compounded TBVPS and upcoming Max Pain.")
