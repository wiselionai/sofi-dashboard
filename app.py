import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime

st.set_page_config(page_title="SOFI Optimizer", layout="centered")
st.title("SOFI TBVPS & Max Pain Optimizer")

# 1. Load Data
@st.cache_data
def load_data():
    return pd.read_excel('daily_tbvps_calculator.xlsx', index_col=0)

df_tbvps = load_data()

# 2. Get Live Price
try:
    ticker = yf.Ticker("SOFI")
    data = ticker.history(period="1d")
    live_price = data['Close'].iloc[-1]
    
    # 3. Calculate TBVPS Multiple
    today = pd.Timestamp.now().normalize()
    # Ensure today's date exists in our data
    if today in df_tbvps.index:
        tbvps = df_tbvps.loc[today, 'TBVPS']
        multiple = live_price / tbvps
        
        # 4. Display Metrics
        col1, col2 = st.columns(2)
        col1.metric("SOFI Price", f"${live_price:.2f}")
        col2.metric("TBVPS Multiple", f"{multiple:.2f}x")
        
        if multiple < 2.0:
            st.success("Multiple < 2.0x: Consider Selling Puts")
        else:
            st.warning("Multiple > 2.0x: Market is Rich")
    else:
        st.write("Data for today is unavailable.")
except Exception as e:
    st.error(f"Error fetching data: {e}")
