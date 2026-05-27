import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

# --- Page Config ---
st.set_page_config(page_title="SOFI Optimizer", layout="centered")
st.title("SOFI TBVPS & Multiple Optimizer")

# --- Logic: Generate TBVPS Data on the fly ---
@st.cache_data
def get_tbvps_data():
    # Based on our 40% annual growth assumption
    start_tbvps = 7.68 
    annual_growth = 0.40
    daily_growth_rate = (1 + annual_growth)**(1/365) - 1
    
    # Generate 365 days from today
    start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    dates = [start_date + timedelta(days=i) for i in range(365)]
    tbvps_values = [start_tbvps * (1 + daily_growth_rate)**i for i in range(365)]
    
    return pd.DataFrame({'TBVPS': tbvps_values}, index=dates)

df_tbvps = get_tbvps_data()

# --- Fetch Live Data ---
try:
    ticker = yf.Ticker("SOFI")
    # Fetching latest price
    hist = ticker.history(period="1d")
    live_price = hist['Close'].iloc[-1]
    
    # Calculate today's TBVPS and Multiple
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    if today in df_tbvps.index:
        tbvps_today = df_tbvps.loc[today, 'TBVPS']
        multiple = live_price / tbvps_today
        
        # Display Metrics
        col1, col2 = st.columns(2)
        col1.metric("SOFI Price", f"${live_price:.2f}")
        col2.metric("TBVPS Multiple", f"{multiple:.2f}x")
        
        # Strategy Logic
        st.write("---")
        if multiple < 2.0:
            st.success("Multiple is below 2.0x. Signal: SELL PUTS (Bullish)")
        else:
            st.warning("Multiple is above 2.0x. Signal: Market is rich, wait for better entry.")
            
    else:
        st.error("Today's date not found in calculation engine.")

except Exception as e:
    st.error(f"Could not fetch live market data: {e}")

# --- Footer ---
st.write("---")
st.caption("Optimizer tracks current SOFI price against the daily compounded 40% annual growth model.")
