import streamlit as st
import yfinance as yf
import pandas as pd

# ---------------------------------------------------------
# 1. Page Configuration & Video Background Setup
# ---------------------------------------------------------
st.set_page_config(
    page_title="USD/LKR & Gold Tracker",
    page_icon="📈",
    layout="wide"
)

# Custom CSS to insert an HTML5 video element behind Streamlit content
video_url = "https://assets.mixkit.co/videos/preview/mixkit-digital-animation-of-screens-with-charts-and-data-31911-large.mp4" # Replace with your direct MP4 URL or local path

background_video_style = f"""
<style>
/* Video Background Element */
#bg-video {{
    position: fixed;
    right: 0;
    bottom: 0;
    min-width: 100%;
    min-height: 100%;
    z-index: -1;
    opacity: 0.25; /* Adjust video transparency here */
    object-fit: cover;
}}

/* Main container readability adjustments */
.stApp {{
    background-color: rgba(14, 17, 23, 0.75);
}}

.block-container {{
    background-color: rgba(255, 255, 255, 0.05);
    border-radius: 10px;
    padding: 2rem;
    backdrop-filter: blur(5px);
}}
</style>

<video autoplay loop muted playsinline id="bg-video">
    <source src="{video_url}" type="video/mp4">
    Your browser does not support HTML5 video.
</video>
"""

# Inject HTML/CSS into Streamlit app
st.markdown(background_video_style, unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. Data Collection (Cached for performance)
# ---------------------------------------------------------
@st.cache_data
def load_data():
    # Download USD to LKR exchange rate data
    usd_lkr = yf.download('USDLKR=X', start='2025-01-01', end='2025-12-31', interval='1wk', auto_adjust=True)
    usd_lkr.reset_index(inplace=True)
    
    # Download Gold rate data
    gold_rate = yf.download('GC=F', start='2025-01-01', end='2025-12-31', interval='1wk', auto_adjust=True)
    gold_rate.reset_index(inplace=True)
    
    # Flatten MultiIndex columns if present from yfinance
    if isinstance(usd_lkr.columns, pd.MultiIndex):
        usd_lkr.columns = [col[0] if col[1] == '' else col[0] for col in usd_lkr.columns]
    if isinstance(gold_rate.columns, pd.MultiIndex):
        gold_rate.columns = [col[0] if col[1] == '' else col[0] for col in gold_rate.columns]

    # Merge DataFrames on Date
    merged_df = pd.merge(usd_lkr, gold_rate, on='Date', suffixes=('_USD_LKR', '_GOLD'), how='inner')
    
    # Extract target columns
    clean_df = merged_df[['Date', 'Close_USD_LKR', 'Close_GOLD']].copy()
    clean_df.columns = ['Date', 'USD/LKR Close', 'Gold Close (USD)']
    
    return clean_df

# Load the dataset
df = load_data()

# ---------------------------------------------------------
# 3. Streamlit Dashboard Layout
# ---------------------------------------------------------
st.title("📊 USD/LKR & Gold Rates Dashboard (2025)")
st.write("Tracking weekly trends for Sri Lankan Rupee Exchange Rates and International Gold Futures.")

# Top Summary Metrics
col1, col2, col3 = st.columns(3)

latest_usd = df['USD/LKR Close'].iloc[-1]
latest_gold = df['Gold Close (USD)'].iloc[-1]

col1.metric("Latest USD / LKR Rate", f"{latest_usd:.2f} LKR")
col2.metric("Latest Gold Price (Futures)", f"${latest_gold:.2f}")
col3.metric("Total Weeks Tracked", f"{len(df)} Weeks")

st.markdown("---")

# Data Visualization
st.subheader("📈 Price Trends")
tab1, tab2 = st.tabs(["USD/LKR Exchange Rate", "Gold Futures Price"])

with tab1:
    st.line_chart(df.set_index('Date')['USD/LKR Close'])

with tab2:
    st.line_chart(df.set_index('Date')['Gold Close (USD)'])

# Raw Data Table
with st.expander("🔍 View Raw Dataset"):
    st.dataframe(df, use_container_width=True)
