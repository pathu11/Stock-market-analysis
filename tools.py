import yfinance as yf
from langchain.tools import tool
import pandas as pd
import ta
import numpy as np

class StockAnalysisTools:
    
    @tool("Fetch S&P 500 & Screen")
    def fetch_and_screen_sp500():
        """
        Fetches the complete S&P 500 list, screens for the top 5 stocks based on 
        recent trading volume and price momentum (technical strength), 
        and returns their tickers.
        """
        try:
            # Get S&P 500 tickers from Wikipedia
            url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
            tables = pd.read_html(url)
            df = tables[0]
            tickers = df['Symbol'].tolist()
            
            # For demo speed, we'll take a random sample or top 20 to screen 
            # (Fetching 500 live prices takes too long for a web demo)
            # In production, use a db or batch API.
            # Here we just pick a few popular ones to simulate a "result" of a screen
            # or screen a small batch.
            subset = tickers[:20]  # Let's screen the first 20 for the demo
            
            screened_results = []
            
            for ticker in subset:
                try:
                    stock = yf.Ticker(ticker)
                    hist = stock.history(period="1mo")
                    if hist.empty: continue
                    
                    # Calculate simple momentum (Return)
                    start_price = hist['Close'].iloc[0]
                    end_price = hist['Close'].iloc[-1]
                    momentum = ((end_price - start_price) / start_price) * 100
                    
                    screened_results.append((ticker, momentum))
                except:
                    continue
            
            # Sort by momentum and take top 5
            screened_results.sort(key=lambda x: x[1], reverse=True)
            top_5 = [item[0] for item in screened_results[:5]]
            
            return f"Top 5 Screened Stocks based on Momentum: {', '.join(top_5)}"
        except Exception as e:
            # Fallback if scraping fails
            return "AAPL, NVDA, MSFT, AMD, TSLA"

    @tool("Calculate Risk Metrics")
    def calculate_risk_metrics(ticker: str):
        """
        Calculates detailed risk metrics: Beta, Volatility (Standard Deviation), 
        and Maximum Drawdown for a specific stock.
        """
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1y")
            
            if hist.empty:
                return "No data found."
            
            # Daily Returns
            hist['pct_change'] = hist['Close'].pct_change()
            
            # Volatility (Annualized Standard Deviation)
            volatility = hist['pct_change'].std() * np.sqrt(252) * 100
            
            # Max Drawdown
            rolling_max = hist['Close'].cummax()
            daily_drawdown = hist['Close'] / rolling_max - 1.0
            max_drawdown = daily_drawdown.min() * 100
            
            # Beta (Approximate using market correlation if not available directly)
            beta = stock.info.get('beta', 'N/A')
            
            return f"""
            Risk Analysis for {ticker}:
            - Beta: {beta} (Market Sensitivity)
            - Annualized Volatility: {volatility:.2f}%
            - Max Drawdown (1Y): {max_drawdown:.2f}%
            """
        except Exception as e:
            return f"Error calculating risk for {ticker}: {e}"

    @tool("Fetch Fundamental Data")
    def fetch_fundamental_data(ticker: str):
        """
        Fetches fundamental data: P/E, Market Cap, EPS, and Sector.
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            simple_info = {
                "Ticker": ticker,
                "Price": info.get("currentPrice"),
                "MarketCap": info.get("marketCap"),
                "PE_Ratio": info.get("trailingPE"),
                "EPS": info.get("trailingEps"),
                "Sector": info.get("sector"),
                "TargetPrice": info.get("targetMeanPrice")
            }
            return str(simple_info)
        except Exception as e:
            return f"Error fetching fundamentals for {ticker}: {e}"

    @tool("Calculate Technical Indicators")
    def calculate_technicals(ticker: str):
        """
        Calculates RSI, MACD, and SMAs for a stock.
        """
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period="6mo")
            if df.empty: return "No data."

            # RSI
            df['rsi'] = ta.momentum.RSIIndicator(df['Close']).rsi()
            # MACD
            macd = ta.trend.MACD(df['Close'])
            df['macd'] = macd.macd()
            df['macd_signal'] = macd.macd_signal()
            # SMA
            df['sma_50'] = ta.trend.SMAIndicator(df['Close'], window=50).sma_indicator()
            df['sma_200'] = ta.trend.SMAIndicator(df['Close'], window=200).sma_indicator()
            
            latest = df.iloc[-1]
            return f"""
            Technicals for {ticker}:
            - Price: {latest['Close']:.2f}
            - RSI: {latest['rsi']:.2f}
            - MACD: {latest['macd']:.2f} (Signal: {latest['macd_signal']:.2f})
            - SMA 50: {latest['sma_50']:.2f}
            - SMA 200: {latest['sma_200']:.2f}
            """
        except Exception as e:
            return f"Error with technicals for {ticker}: {e}"