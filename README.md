# ⚡ Stock Insights AI - Multi-Agent Research Terminal

Stock Insights AI is an advanced financial analytics platform powered by CrewAI and Google Gemini 2.5 Flash. It utilizes a multi-agent system to perform deep-dive equity research and real-time market trend scanning, mimicking the workflow of a professional hedge fund investment committee.

You can try the live app here: [Stock Insights AI on Streamlit](https://agenticstockanalysis.streamlit.app/)

---

## 🚀 Features

### 1. Single Ticker Deep Dive
- **4-Agent Crew:** Sentiment Analyst, Fundamental Analyst, Technical Analyst, and Portfolio Manager.
- **Comprehensive Report:** Generates a structured investment memo with "Buy/Sell/Hold" recommendations.
- **Live Data:** Real-time price charts, P/E ratios, Market Cap, and Volatility metrics via Yahoo Finance.
- **Sentiment Analysis:** Analyzes news headlines using Alpha Vantage to gauge market mood.

### 2. Market Trend Scanner
- **Automated Screening:** Instantly fetches the day's Top Gainers using Alpha Vantage API.
- **Strategic Analysis:** Uses a specialized 2-Agent Crew to explain why stocks are moving and provide short-term trading signals.
- **Visual Dashboard:** Interactive metric cards showing % returns and price movement.

---

## 🛠️ Tech Stack

- **Core Framework:** Python 3.13
- **AI Orchestration:** CrewAI (Multi-Agent Framework)
- **LLM Engine:** Google Gemini 2.5 Flash (via litellm)
- **Frontend:** Streamlit (Custom CSS for Dark/Neon Glassmorphism UI)
- **Data Sources:**
  - Yahoo Finance (`yfinance`): Price history, technical indicators, fundamental data.
  - Alpha Vantage: News sentiment, top market movers list.
- **Visualization:** Plotly (Interactive Candlestick charts)

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.13 installed
- Google Gemini API Key (Free tier available at Google AI Studio)
- Alpha Vantage API Key (Free tier available at Alpha Vantage)

### Step 1: Clone the Repository
```bash
git clone https://github.com/pathu11/Stock-market-analysis.git
cd Stock-market-analysis 
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```
### Step 3: Install Dependencies
``` bash
pip install -r requirements.txt
```
### Step 4: Configure Environment Variables
Create a file named .env in the root directory and add your keys:
```bash 
# .env file
GOOGLE_API_KEY=your_google_gemini_key_here
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here
```
### Step 5: Run the Application
```bash
streamlit run app.py
```
The application will launch in your browser at http://localhost:8501.

## 📂 Project Structure
``` bash
stock-insights-ai/
│
├── agents.py             # Defines the CrewAI Agents, Tasks, and LLM configuration
├── tools.py              # Custom tools for fetching data (YFinance, Alpha Vantage)
├── app.py                # Main Streamlit UI application
├── requirements.txt      # Python dependencies
├── .env                  # API Keys (Not committed to repo)
└── README.md             # Documentation
```



## ⚠️ Important Note on API Limits

- Alpha Vantage Free Tier: Limited to 25 requests per day. Use the "Market Scanner" sparingly on the free tier.
