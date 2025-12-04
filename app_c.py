import streamlit as st
from agents import create_single_stock_crew
import os
from dotenv import load_dotenv
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import re
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Page Config
st.set_page_config(page_title="Stock Intelligence", page_icon="⚡", layout="wide")

# 1. HERO SECTION (Title & Search)
st.markdown("<h1 style='text-align: center; margin-bottom: 10px;'>Stock Intelligence</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #6b7280; margin-bottom: 40px;'>Get comprehensive AI-driven analysis with key metrics, risk assessment, and actionable insights.</p>", unsafe_allow_html=True)


# --- CUSTOM CSS (Creative UI) ---
st.markdown("""
<style>
    /* Main Background & Fonts */
    .stApp {
        background: linear-gradient(to bottom right, #0e1117, #161b22);
    }
    h1, h2, h3 {
        font-family: 'Helvetica Neue', sans-serif;
        color: #e6e6e6 !important;
    }
    
    /* Metric Cards (Glassmorphism) */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        padding: 15px;
        border-radius: 12px;
        transition: transform 0.2s;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        border-color: rgba(255, 255, 255, 0.3);
    }
    div[data-testid="stMetric"] label {
        color: #a0a0a0 !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-weight: 600;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0d1117;
        border-right: 1px solid #30363d;
    }
    
    /* Custom Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #238636 0%, #2ea043 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        box-shadow: 0 4px 12px rgba(46, 160, 67, 0.4);
        transform: scale(1.02);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255,255,255,0.05);
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        color: #c9d1d9;
    }
    .stTabs [aria-selected="true"] {
        background-color: #238636 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "market_data" not in st.session_state:
    st.session_state.market_data = None
if "current_ticker" not in st.session_state:
    st.session_state.current_ticker = ""

# --- SIDEBAR CONFIGURATION ---
with st.sidebar:
    st.title("⚙️ Control Center")
    
    # API Key Handling
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        st.error("⚠️ GOOGLE_API_KEY missing in .env")
        st.stop()
    else:
        st.markdown(f"✅ **System Status:** Online")
        # st.markdown(f"🔑 **License:** Active (Gemini)")
    
    st.markdown("---")
    
    # Inputs
    ticker = st.text_input("Stock Ticker", value="AAPL", placeholder="e.g. NVDA").upper()
    
    st.markdown("### 📅 Analysis Period")
    today = datetime.now().date()
    default_start = today - timedelta(days=365)
    
    start_date = st.date_input("Start Date", default_start)
    end_date = st.date_input("End Date", today)
    
    if start_date > end_date:
        st.error("Error: End Date must be after Start Date.")
    
    st.markdown("---")
    run_btn = st.button("🚀 Initialize Analysis", type="primary", use_container_width=True)
    
    # Reset Button
    if st.button("🔄 Reset System", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# --- MAIN APP LOGIC ---

# st.title("🏦 AI Equity Research Terminal")
# st.caption(f"Powered by Multi-Agent Architecture | Gemini 1.5 Flash")

# 1. TRIGGER ANALYSIS
if run_btn and ticker:
    if start_date > end_date:
        st.toast("⚠️ Invalid Date Range", icon="❌")
    else:
        with st.status("🤖 Orchestrating AI Agents...", expanded=True) as status:
            try:
                # A. Fetch Market Data
                status.write("📡 Connecting to Market Data Feed...")
                stock = yf.Ticker(ticker)
                hist = stock.history(start=start_date, end=end_date)
                info = stock.info
                
                if hist.empty:
                    st.error(f"Could not fetch data for {ticker}. Check symbol/dates.")
                    st.stop()
                
                # Store market data in session
                st.session_state.market_data = {
                    "hist": hist,
                    "info": info,
                    "ticker": ticker
                }
                
                # B. Run CrewAI
                status.write("🧠 Waking up Analyst Agents...")
                status.write("🔍 Fundamental Analyst auditing reports...")
                status.write("📉 Technical Analyst measuring trends...")
                status.write("🛡️ Risk Officer running simulations...")
                
                crew = create_single_stock_crew(ticker, api_key)
                result = crew.kickoff()
                
                # Store analysis in session
                st.session_state.analysis_result = str(result)
                st.session_state.current_ticker = ticker
                
                status.write("✅ Analysis Finalized.")
                status.update(label="Mission Complete", state="complete", expanded=False)
                
            except Exception as e:
                st.error(f"Critical Failure: {e}")
                st.stop()

# 2. DISPLAY RESULTS (From Session State)
if st.session_state.analysis_result and st.session_state.market_data:
    
    # Load data from state
    data = st.session_state.market_data
    hist = data["hist"]
    info = data["info"]
    result_text = st.session_state.analysis_result
    active_ticker = st.session_state.current_ticker

    # Header Stats
    st.markdown(f"## {info.get('shortName', active_ticker)} ({active_ticker})")
    
    col1, col2, col3, col4 = st.columns(4)
    current_price = info.get('currentPrice', hist['Close'].iloc[-1])
    prev_close = info.get('previousClose', hist['Close'].iloc[-2]) if len(hist) > 1 else current_price
    delta = current_price - prev_close
    delta_percent = (delta / prev_close) * 100

    col1.metric("Current Price", f"${current_price:,.2f}", f"{delta:+.2f} ({delta_percent:+.2f}%)")
    col2.metric("Market Cap", f"${info.get('marketCap', 0):,}")
    col3.metric("Beta (Volatility)", f"{info.get('beta', 'N/A')}")
    col4.metric("52W High", f"${info.get('fiftyTwoWeekHigh', 0)}")

    # TABS LAYOUT
    tab1, tab2, tab3 = st.tabs(["📉 Market Overview", "🧠 AI Deep Dive", "📝 Raw Data"])

    # TAB 1: Charts
    with tab1:
        st.subheader("Price Action Analysis")
        fig = go.Figure(data=[go.Candlestick(x=hist.index,
                        open=hist['Open'],
                        high=hist['High'],
                        low=hist['Low'],
                        close=hist['Close'])])
        fig.update_layout(
            template="plotly_dark",
            height=500,
            xaxis_rangeslider_visible=False,
            margin=dict(l=0, r=0, t=0, b=0),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)

    # TAB 2: AI Report
    with tab2:
        # Parse Recommendation
        rec_match = re.search(r"Recommendation:\*\*?\s*(.*)", result_text, re.IGNORECASE)
        confidence_match = re.search(r"Confidence Score:\*\*?\s*(\d+%)", result_text, re.IGNORECASE)
        
        rec_text = rec_match.group(1).strip() if rec_match else "N/A"
        confidence_text = confidence_match.group(1).strip() if confidence_match else "N/A"

        # Dynamic Color Logic
        if "BUY" in rec_text.upper():
            banner_color = "linear-gradient(90deg, #1e4620 0%, #0f1f10 100%)"
            border_color = "#4ade80"
            icon = "🚀"
        elif "SELL" in rec_text.upper():
            banner_color = "linear-gradient(90deg, #450a0a 0%, #200505 100%)"
            border_color = "#f87171"
            icon = "⚠️"
        else:
            banner_color = "linear-gradient(90deg, #422006 0%, #1f1002 100%)"
            border_color = "#facc15"
            icon = "⚖️"

        # Executive Summary Banner
        st.markdown(f"""
        <div style="
            background: {banner_color};
            padding: 25px;
            border-radius: 15px;
            border: 2px solid {border_color};
            margin-bottom: 25px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        ">
            <h2 style="color: white; margin:0; font-size: 28px;">{icon} Verdict: {rec_text}</h2>
            <p style="color: #d1d5db; margin: 10px 0 0 0; font-size: 18px;">
                <strong>Confidence Score:</strong> <span style="color: {border_color}">{confidence_text}</span>
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### 📑 Comprehensive Analysis")
        st.markdown(result_text)
        
        # Download Button inside the tab
        st.download_button(
            label="📥 Download Full Report",
            data=result_text,
            file_name=f"{active_ticker}_Analysis_{datetime.now().strftime('%Y-%m-%d')}.txt",
            mime="text/plain",
            help="Save this analysis as a text file"
        )

    # TAB 3: Raw Data
    with tab3:
        st.subheader("Historical Data")
        st.dataframe(hist, use_container_width=True)
        st.subheader("Company Info")
        st.json(info)

elif not run_btn and not st.session_state.analysis_result:
    # Landing Page State
    st.info("👈 Enter a stock ticker in the sidebar and click 'Run Analysis' to begin.")
