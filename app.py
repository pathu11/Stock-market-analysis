import streamlit as st
from agents import create_single_stock_crew
import os
from dotenv import load_dotenv
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# Load environment variables
load_dotenv()

# Page Config
st.set_page_config(page_title="AI Stock Analyst", page_icon="📈", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 10px;
    }
    /* Force text to black so it is visible on the light background */
    .stMetric > div {
        color: #000000 !important;
    }
    /* Optional: Ensure the label (top text) is also black */
    .stMetric label {
        color: #000000 !important;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Control Panel")
    st.info("This tool performs a deep-dive analysis on a single stock using 4 AI Agents.")
    
    # Securely fetch API Key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        st.error("⚠️ GOOGLE_API_KEY not found in .env")
        st.stop()
    
    st.success("API Key Loaded Securely")

# Main Content
st.title("📈 Single Stock AI Analyst")
st.markdown("### Powered by Gemini 1.5 Flash")

# Input Section
col1, col2 = st.columns([3, 1])
with col1:
    ticker = st.text_input("Enter Stock Ticker", placeholder="e.g. AAPL, NVDA, TSLA", value="AAPL").upper()
with col2:
    run_btn = st.button("🚀 Analyze Stock", use_container_width=True)

if run_btn and ticker:
    
    # 1. Fetch & Display Live Market Data FIRST (Fast Feedback)
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="6mo")
        info = stock.info
        
        if hist.empty:
            st.error("No data found for this ticker.")
            st.stop()

        # Display Metrics
        st.divider()
        m1, m2, m3, m4 = st.columns(4)
        current_price = info.get('currentPrice', hist['Close'].iloc[-1])
        prev_close = info.get('previousClose', hist['Close'].iloc[-2])
        delta = current_price - prev_close
        
        m1.metric("Current Price", f"${current_price:.2f}", f"{delta:.2f}")
        m2.metric("Market Cap", f"${info.get('marketCap', 0):,}")
        m3.metric("P/E Ratio", f"{info.get('trailingPE', 'N/A')}")
        m4.metric("52W High", f"${info.get('fiftyTwoWeekHigh', 0)}")

        # Interactive Chart (Candlestick)
        fig = go.Figure(data=[go.Candlestick(x=hist.index,
                        open=hist['Open'],
                        high=hist['High'],
                        low=hist['Low'],
                        close=hist['Close'])])
        fig.update_layout(title=f"{ticker} Price History (6 Months)", xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.warning(f"Could not load live market data: {e}")

    # 2. Run AI Analysis (Slower Process)
    st.divider()
    st.subheader(f"🤖 AI Crew Analysis for {ticker}")
    
    with st.status("Initializing Agents...", expanded=True) as status:
        try:
            # Initialize Crew
            status.write("🧠 Waking up Analyst Agents...")
            crew = create_single_stock_crew(ticker, api_key)
            
            status.write(f"🔍 Fundamental Analyst is reading {ticker} balance sheets...")
            status.write(f"📉 Technical Analyst is measuring {ticker} trends...")
            status.write(f"🛡️ Risk Officer is calculating volatility...")
            
            # Run the Crew
            result = crew.kickoff()
            
            status.write("✅ Portfolio Manager has finalized the report.")
            status.update(label="Analysis Complete", state="complete", expanded=False)

            # Display Final Report
            st.markdown(result)

        except Exception as e:
            st.error(f"AI Analysis Failed: {e}")
            st.info("Try waiting 60 seconds (Free Tier Limits) or check your API key.")