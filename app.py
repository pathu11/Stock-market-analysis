import streamlit as st
from agents import create_single_stock_crew, create_market_scanner_crew
import os
from dotenv import load_dotenv
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import re
import requests
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Page Config
st.set_page_config(page_title="Stock Insights AI", page_icon="⚡", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .stApp { background-color: #050505; background-image: radial-gradient(circle at 50% 0%, #1a1a2e 0%, #050505 60%); color: #e0e0e0; }
    .metric-card { background-color: #0f1116; border: 1px solid #1e2128; border-radius: 12px; padding: 20px; }
    .stButton>button { background-color: #3b82f6; color: white; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# --- HELPER: ALPHA VANTAGE FETCHER ---
def fetch_top_gainers(api_key):
    """Fetches top gainers directly from Alpha Vantage API"""
    url = f"https://www.alphavantage.co/query?function=TOP_GAINERS_LOSERS&apikey={api_key}"
    try:
        response = requests.get(url)
        data = response.json()
        if "top_gainers" in data:
            return data["top_gainers"][:5] # Return top 5
        return []
    except:
        return []

# --- STATE MANAGEMENT ---
if "single_analysis" not in st.session_state: st.session_state.single_analysis = None
if "scanner_report" not in st.session_state: st.session_state.scanner_report = None
if "current_ticker" not in st.session_state: st.session_state.current_ticker = None

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚡ Control Center")
    
    # Keys from .env ONLY
    google_key = os.getenv("GOOGLE_API_KEY")
    av_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    
    if not google_key:
        st.error("⚠️ Missing GOOGLE_API_KEY in .env")
        st.stop()
    
    if not av_key:
        st.error("⚠️ Missing ALPHA_VANTAGE_KEY in .env")
        st.stop()

    st.success("✅ API Keys Loaded")
    st.markdown("---")
    
    app_mode = st.radio("Select Mode:", ["Single Ticker Analysis", "Market Trend Scanner"])

# --- MAIN APP ---

if app_mode == "Single Ticker Analysis":
    st.markdown("## 📈 Deep Dive Analysis")
    
    # Inputs
    ticker = st.text_input("Stock Ticker", value="AAPL").upper()
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime.now() - timedelta(days=180))
    with col2:
        end_date = st.date_input("End Date", datetime.now())

    if st.button("🚀 Analyze Stock"):
        # Reset previous session data if ticker changes or new run requested
        st.session_state.single_analysis = None
        st.session_state.current_ticker = ticker
        
        with st.status("🤖 AI Agents Working...", expanded=True) as status:
            try:
                # 1. Run Crew
                status.write(f"🧠 Analyzing {ticker} from {start_date} to {end_date}...")
                
                # Pass dates to the crew
                crew = create_single_stock_crew(ticker, str(start_date), str(end_date), google_key, av_key)
                result = crew.kickoff()
                
                st.session_state.single_analysis = str(result)
                status.update(label="Complete", state="complete", expanded=False)
            except Exception as e:
                st.error(f"Error: {e}")

    # Display Analysis
    if st.session_state.single_analysis:
        st.markdown(f"### Analysis Report: {st.session_state.current_ticker}")
        st.markdown(st.session_state.single_analysis)
        
        st.download_button(
            label="📥 Download Report",
            data=st.session_state.single_analysis,
            file_name=f"{st.session_state.current_ticker}_report.txt",
            mime="text/plain"
        )

elif app_mode == "Market Trend Scanner":
    st.markdown("## 🌍 Real-Time Market Scanner")
    st.info("Fetches Top Gainers from Alpha Vantage and analyzes them.")
    
    if st.button("🔍 Scan Top Gainers"):
        # Clear previous scan results
        st.session_state.scanner_report = None
        
        with st.status("Scanning Market...", expanded=True) as status:
            try:
                status.write("📡 Fetching Top Gainers from Alpha Vantage...")
                gainers_data = fetch_top_gainers(av_key)
                
                if not gainers_data:
                    st.error("Failed to fetch gainers (Check API Key or Limit). Using fallback.")
                    top_tickers = ['NVDA', 'TSLA', 'AMD'] # Fallback
                else:
                    top_tickers = [g['ticker'] for g in gainers_data]
                    # Display Gainers
                    cols = st.columns(len(top_tickers))
                    for i, t in enumerate(top_tickers):
                        cols[i].metric(t, f"+{gainers_data[i]['change_percentage']}")

                status.write(f"🧠 AI Analyzing: {', '.join(top_tickers)}")
                crew = create_market_scanner_crew(top_tickers, google_key)
                report = crew.kickoff()
                st.session_state.scanner_report = str(report)
                
                status.update(label="Complete", state="complete", expanded=False)
            except Exception as e:
                st.error(f"Scan Error: {e}")

    if st.session_state.scanner_report:
        st.markdown("### 🧠 Strategic Analysis")
        # Color coding logic
        report_html = st.session_state.scanner_report.replace("Signal: BUY", "Signal: <span style='color:#4ade80;font-weight:bold'>BUY</span>")
        report_html = report_html.replace("Signal: PROFIT-TAKE", "Signal: <span style='color:#f87171;font-weight:bold'>PROFIT-TAKE</span>")
        report_html = report_html.replace("Signal: HOLD", "Signal: <span style='color:#facc15;font-weight:bold'>HOLD</span>")
        
        st.markdown(report_html, unsafe_allow_html=True)