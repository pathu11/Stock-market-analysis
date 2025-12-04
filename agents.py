from crewai import Agent, Task, Crew, Process
from tools import StockAnalysisTools
from langchain_google_genai import ChatGoogleGenerativeAI
import os

def create_market_scanner_crew(google_api_key: str):
    
    # --- LLM CONFIGURATION (GEMINI) ---
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        verbose=True,
        temperature=0.5,
        google_api_key=google_api_key
    )

    # --- AGENTS ---

    # 1. The Screener
    screener_agent = Agent(
        role='Chief Market Screener',
        goal='Identify the top 5 investable stocks from the S&P 500 based on momentum.',
        backstory="You are an algorithm-driven trader. You scan the market to find the top 5 stocks with the highest momentum and volume.",
        verbose=True,
        allow_delegation=False,
        tools=[StockAnalysisTools.fetch_and_screen_sp500],
        llm=llm
    )

    # 2. Fundamental Analyst
    fundamental_agent = Agent(
        role='Senior Fundamental Analyst',
        goal='Analyze the financial health of the 5 screened stocks.',
        backstory="You are a value investor. You check P/E ratios, earnings growth, and debt levels. You are thorough.",
        verbose=True,
        allow_delegation=False,
        tools=[StockAnalysisTools.fetch_fundamental_data],
        llm=llm
    )

    # 3. Technical Analyst
    technical_agent = Agent(
        role='Chief Technical Analyst',
        goal='Analyze the technical indicators (RSI, MACD) for the 5 screened stocks.',
        backstory="You are a expert chartist. You look for trend confirmations and entry points.",
        verbose=True,
        allow_delegation=False,
        tools=[StockAnalysisTools.calculate_technicals],
        llm=llm
    )

    # 4. Risk Analyst
    risk_agent = Agent(
        role='Chief Risk Officer',
        goal='Evaluate risk metrics (Beta, Volatility) for the 5 screened stocks.',
        backstory="You are a risk manager. You calculate volatility and max drawdown to ensure capital preservation.",
        verbose=True,
        allow_delegation=False,
        tools=[StockAnalysisTools.calculate_risk_metrics],
        llm=llm
    )

    # 5. Portfolio Manager
    manager_agent = Agent(
        role='Portfolio Manager',
        goal='Synthesize all analysis into a final ranked list with scores.',
        backstory="You are the lead portfolio manager. You take the raw analysis from your team and assign numerical scores.",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    # --- TASKS ---

    task_screen = Task(
        description="""
        Fetch the S&P 500 list and identify the top 5 candidates based on momentum and volume using the screening tool.
        Your output MUST be a clean, comma-separated list of just the 5 tickers.
        Example Output: AAPL, NVDA, MSFT, AMD, TSLA
        """,
        expected_output="A comma-separated list of 5 stock tickers.",
        agent=screener_agent
    )

    task_fundamentals = Task(
        description="""
        You will receive a list of 5 stock tickers from the Screener.
        For EACH ticker in that list, you MUST call the 'Fetch Fundamental Data' tool.
        Do not summarize until you have fetched data for ALL 5 stocks.
        """,
        expected_output="A detailed summary of fundamental metrics for ALL 5 stocks.",
        agent=fundamental_agent,
        context=[task_screen]
    )

    task_technicals = Task(
        description="""
        You will receive a list of 5 stock tickers from the Screener.
        For EACH ticker in that list, you MUST call the 'Calculate Technical Indicators' tool.
        Do not summarize until you have calculated indicators for ALL 5 stocks.
        """,
        expected_output="A detailed summary of technical indicators for ALL 5 stocks.",
        agent=technical_agent,
        context=[task_screen]
    )

    task_risk = Task(
        description="""
        You will receive a list of 5 stock tickers from the Screener.
        For EACH ticker in that list, you MUST call the 'Calculate Risk Metrics' tool.
        Do not summarize until you have calculated risk metrics for ALL 5 stocks.
        """,
        expected_output="A detailed summary of risk metrics for ALL 5 stocks.",
        agent=risk_agent,
        context=[task_screen]
    )

    task_rank = Task(
        description="""
        You have received detailed reports from the Fundamental Analyst, Technical Analyst, and Risk Officer for 5 specific stocks.
        
        Your task is to:
        1. Review the data for each stock.
        2. Assign a score (0-100) for Technicals, Fundamentals, and Risk.
        3. Calculate a Total Score (Average of the three).
        4. Rank the 5 stocks from #1 (Best) to #5 (Worst).

        Output the final report in this EXACT format for each stock:

        Stock: [Ticker Symbol]
        - Total Score: [0-100]
        - Investment Recommendation: [Strong Buy/Buy/Hold/Sell]
        - Technical Analysis Score: [0-100]
        - Fundamental Analysis Score: [0-100]
        - Risk Assessment Score: [0-100]
        - Analysis: [A concise 2-sentence explanation of why it received this score]
        """,
        expected_output="A ranked list of 5 stocks with detailed scores and analysis.",
        agent=manager_agent,
        context=[task_fundamentals, task_technicals, task_risk]
    )

    # --- CREW ---
    
    crew = Crew(
        agents=[screener_agent, fundamental_agent, technical_agent, risk_agent, manager_agent],
        tasks=[task_screen, task_fundamentals, task_technicals, task_risk, task_rank],
        process=Process.sequential,
        verbose=True
    )

    return crew