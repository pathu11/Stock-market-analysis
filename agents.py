# from crewai import Agent, Task, Crew, Process, LLM
# from tools import StockAnalysisTools
# import os

# def create_single_stock_crew(ticker: str, google_api_key: str):
    
#     # --- LLM CONFIGURATION ---
#     llm = LLM(
#         model="gemini/gemini-2.5-flash",
#         api_key=google_api_key,
#         temperature=0.3, # Lower temperature for more factual analysis
#         verbose=True
#     )

#     # --- AGENTS ---

#     # 1. Fundamental Analyst
#     fundamental_agent = Agent(
#         role='Senior Fundamental Analyst',
#         goal=f'Analyze the financial health and intrinsic value of {ticker}.',
#         backstory="You are a value investor like Warren Buffett. You dig into P/E ratios, earnings growth, and market cap to determine if a stock is undervalued.",
#         verbose=True,
#         allow_delegation=False,
#         tools=[StockAnalysisTools.fetch_fundamental_data],
#         llm=llm
#     )

#     # 2. Technical Analyst
#     technical_agent = Agent(
#         role='Chief Technical Analyst',
#         goal=f'Analyze the price action and trends of {ticker}.',
#         backstory="You are a expert chartist. You look for support/resistance, RSI levels, and MACD crossovers to find the best entry points.",
#         verbose=True,
#         allow_delegation=False,
#         tools=[StockAnalysisTools.calculate_technicals],
#         llm=llm
#     )

#     # 3. Risk Analyst
#     risk_agent = Agent(
#         role='Chief Risk Officer',
#         goal=f'Evaluate the volatility and downside risk of {ticker}.',
#         backstory="You are a pessimist. You calculate Beta, Max Drawdown, and volatility to warn investors of potential losses.",
#         verbose=True,
#         allow_delegation=False,
#         tools=[StockAnalysisTools.calculate_risk_metrics],
#         llm=llm
#     )

#     # 4. Portfolio Manager
#     manager_agent = Agent(
#         role='Portfolio Manager',
#         goal=f'Synthesize a final investment decision for {ticker}.',
#         backstory="You make the final call. You combine the fundamental, technical, and risk reports into a clear Buy, Sell, or Hold recommendation.",
#         verbose=True,
#         allow_delegation=False,
#         llm=llm
#     )

#     # --- TASKS ---

#     task_fundamentals = Task(
#         description=f"""
#         Fetch the fundamental data for {ticker} (P/E, Market Cap, EPS, Sector).
#         Analyze the company's valuation compared to the general market.
#         """,
#         expected_output=f"A summary of {ticker}'s fundamental health and valuation.",
#         agent=fundamental_agent
#     )

#     task_technicals = Task(
#         description=f"""
#         Calculate technical indicators for {ticker} (RSI, MACD, Moving Averages).
#         Identify the current trend (Bullish/Bearish/Neutral) and any key support/resistance levels.
#         """,
#         expected_output=f"A technical analysis report for {ticker} with trend identification.",
#         agent=technical_agent
#     )

#     task_risk = Task(
#         description=f"""
#         Calculate risk metrics for {ticker} (Beta, Volatility, Max Drawdown).
#         Assess if this stock is Low, Medium, or High risk for a conservative investor.
#         """,
#         expected_output=f"A risk assessment for {ticker}.",
#         agent=risk_agent
#     )

#     task_report = Task(
#         description=f"""
#         Review the reports from the Fundamental, Technical, and Risk analysts for {ticker}.
        
#         Generate a Final Investment Report formatted exactly like this:
        
#         # Investment Report: {ticker}
        
#         ## 1. Executive Summary
#         **Recommendation:** [STRONG BUY / BUY / HOLD / SELL / STRONG SELL]
#         **Confidence Score:** [0-100]%
#         *(One paragraph summary of why)*

#         ## 2. Detailed Analysis
#         * **Fundamentals:** [Key insights on valuation]
#         * **Technicals:** [Key insights on price action]
#         * **Risk Profile:** [Risk assessment]

#         ## 3. Key Levels
#         * **Target Entry Price:** [Price]
#         * **Stop Loss:** [Price]
#         """,
#         expected_output=f"A comprehensive investment report for {ticker}.",
#         agent=manager_agent,
#         context=[task_fundamentals, task_technicals, task_risk]
#     )

#     # --- CREW ---
    
#     crew = Crew(
#         agents=[fundamental_agent, technical_agent, risk_agent, manager_agent],
#         tasks=[task_fundamentals, task_technicals, task_risk, task_report],
#         process=Process.sequential,
#         verbose=True,
#         max_rpm=10 # Higher RPM allowed since we are only doing 1 stock
#     )

#     return crew
from crewai import Agent, Task, Crew, Process, LLM
from tools import StockAnalysisTools
import os

# --- SHARED LLM CONFIGURATION ---
def get_gemini_llm(api_key):
    return LLM(
        model="gemini/gemini-2.5-flash",
        api_key=api_key,
        temperature=0.2, # Lower temp for financial accuracy
        verbose=True
    )

# --- CREW 1: SINGLE STOCK DEEP DIVE (Updated with Date Range) ---
def create_single_stock_crew(ticker: str, start_date: str, end_date: str, google_api_key: str, alpha_vantage_key: str):
    llm = get_gemini_llm(google_api_key)

    # 1. Sentiment Analyst
    sentiment_agent = Agent(
        role='Senior Sentiment Analyst',
        goal=f'Analyze the market sentiment and news coverage for {ticker} between {start_date} and {end_date}.',
        backstory="You are an expert in behavioral finance. You analyze news headlines and sentiment scores to understand the market's psychological state.",
        verbose=True,
        allow_delegation=False,
        tools=[StockAnalysisTools.fetch_news_sentiment], 
        llm=llm
    )

    # 2. Fundamental Analyst
    fundamental_agent = Agent(
        role='Fundamental Analyst',
        goal=f'Evaluate the financial health of {ticker} within the context of {start_date} to {end_date}.',
        backstory="You are a value investor focused on balance sheets, earnings, and growth metrics.",
        verbose=True,
        allow_delegation=False,
        tools=[StockAnalysisTools.fetch_fundamental_data],
        llm=llm
    )

    # 3. Technical Analyst
    technical_agent = Agent(
        role='Technical Analyst',
        goal=f'Analyze price trends for {ticker} during the period {start_date} to {end_date}.',
        backstory="You are a chartist focused on RSI, MACD, and price action.",
        verbose=True,
        allow_delegation=False,
        tools=[StockAnalysisTools.calculate_technicals],
        llm=llm
    )

    # 4. Portfolio Manager
    manager_agent = Agent(
        role='Portfolio Manager',
        goal=f'Synthesize all reports into a final recommendation for {ticker}.',
        backstory="You make the final investment decision based on sentiment, fundamentals, and technicals.",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    # --- TASKS ---
    
    task_sentiment = Task(
        description=f"""
        Fetch the news sentiment for {ticker}. 
        Use the 'Fetch News Sentiment' tool. 
        **IMPORTANT**: Pass the API Key '{alpha_vantage_key}' as the second argument to the tool.
        Analyze if the sentiment during {start_date} to {end_date} supports a bullish or bearish thesis.
        """,
        expected_output="A summary of market sentiment (Bullish/Bearish) and key headlines.",
        agent=sentiment_agent
    )

    task_fundamentals = Task(
        description=f"Fetch fundamental data for {ticker} (P/E, Market Cap). Context: Analysis period {start_date} to {end_date}.",
        expected_output="Fundamental analysis report.",
        agent=fundamental_agent
    )
    
    task_technicals = Task(
        description=f"Calculate technical indicators for {ticker}. Focus on trends relevant to the window {start_date} to {end_date}.",
        expected_output="Technical analysis report.",
        agent=technical_agent
    )

    task_report = Task(
        description=f"""
        Generate a Final Investment Report for {ticker} covering {start_date} to {end_date}.
        
        Sections:
        1. **Executive Summary**: Recommendation (BUY/SELL/HOLD) & Confidence Score.
        2. **Sentiment Analysis**: What is the news saying?
        3. **Fundamental Health**: Is the company strong?
        4. **Technical Outlook**: What does the chart say?
        """,
        expected_output="Comprehensive investment report.",
        agent=manager_agent,
        context=[task_sentiment, task_fundamentals, task_technicals]
    )

    return Crew(
        agents=[sentiment_agent, fundamental_agent, technical_agent, manager_agent],
        tasks=[task_sentiment, task_fundamentals, task_technicals, task_report],
        process=Process.sequential,
        verbose=True,
        max_rpm=5
    )

# --- CREW 2: MARKET SCANNER ---
def create_market_scanner_crew(top_stocks: list, google_api_key: str):
    llm = get_gemini_llm(google_api_key)
    
    stocks_str = ", ".join(top_stocks)

    trend_agent = Agent(
        role='Market Strategist',
        goal=f'Analyze the top market movers: {stocks_str}.',
        backstory="You analyze why stocks are moving today. You provide a buy/sell/hold verdict for short-term traders.",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    task_summary = Task(
        description=f"""
        The following stocks are today's Top Gainers: {stocks_str}.
        
        For EACH stock, provide a brief analysis and a trading signal.
        Format EXACTLY as:
        
        ### Stock: [Ticker]
        * **Signal:** [BUY / HOLD / PROFIT-TAKE]
        * **Reason:** [1 sentence explanation]
        """,
        expected_output="Strategic report for top movers.",
        agent=trend_agent
    )

    return Crew(
        agents=[trend_agent],
        tasks=[task_summary],
        process=Process.sequential,
        verbose=True,
        max_rpm=5
    )