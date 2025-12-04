import streamlit as st
from agents import create_market_scanner_crew
import os
from dotenv import load_dotenv
import yfinance as yf
import re
import pandas as pd

# Load environment variables
load_dotenv()

# Page Config
st.set_page_config(page_title="S&P 500 AI Scanner", page_icon="🏦", layout="wide")

# CSS for better tables
st.markdown("""
<style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Control Panel")
    st.info("This system scans the S&P 500, filters the top 5 momentum candidates, and performs a deep 5-agent analysis.")
    st.markdown("---")
    st.caption("API Key loaded securely from .env")

# Main Content
st.title("🏦 S&P 500 Intelligent Scanner")
st.markdown("### Powered by Multi-Agent AI (Gemini 1.5 Flash)")

# 1. Securely fetch API Key
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("⚠️ GOOGLE_API_KEY not found! Please create a .env file and add your key.")
    st.code("GOOGLE_API_KEY=AIzaSy...", language="bash")
    st.stop()

if st.button("🚀 Start Market Scan & Analysis"):
    with st.status("🤖 AI Crew is working...", expanded=True) as status:
        try:
            # Initialize Crew
            st.write("Initializing Agents (Gemini Powered)...")
            crew = create_market_scanner_crew(api_key)
            
            st.write("🔍 Phase 1: Screening S&P 500 for candidates...")
            
            # Run the Crew
            result = crew.kickoff()
            
            st.write("✅ Analysis Complete!")
            status.update(label="Analysis Finished", state="complete", expanded=False)

            # --- DISPLAY RESULTS ---
            st.divider()
            
            # 1. Text Report
            st.subheader("🏆 Top 5 Ranked Stocks")
            st.markdown(result)
            
            # 2. Extract Tickers for Charting
            # Regex to find "Stock: [AAPL]" or "Stock: AAPL" patterns in the report
            # The pattern looks for "Stock:" followed by optional spaces and brackets, then the ticker
            tickers = re.findall(r"Stock:\s*\[?([A-Z]+)\]?", str(result))
            
            # Remove duplicates and limit to top 5 just in case
            tickers = list(dict.fromkeys(tickers))[:5]
            
            if tickers:
                st.divider()
                st.subheader(f"📈 Price Performance (Last 30 Days)")
                st.caption(f"Comparing: {', '.join(tickers)}")
                
                # Fetch data
                try:
                    data = yf.download(tickers, period="1mo", progress=False)['Close']
                    
                    # Normalize data (Percentage change from start) for better comparison
                    if not data.empty:
                        normalized_data = ((data - data.iloc[0]) / data.iloc[0]) * 100
                        st.line_chart(normalized_data)
                        st.caption("Y-Axis: Percentage Return (%)")
                    else:
                        st.warning("No price data found for charting.")
                        
                except Exception as e:
                    st.warning(f"Could not load chart data: {e}")

            # 3. Dashboard Metrics
            st.divider()
            st.markdown("### 📊 Rapid Compare")
            col1, col2, col3 = st.columns(3)
            col1.metric("Agents Deployed", "5")
            col2.metric("Stocks Analyzed", "5 (Deep Dive)")
            col3.metric("LLM Model", "Gemini 1.5 Flash")

        except Exception as e:
            st.error(f"An error occurred: {e}")