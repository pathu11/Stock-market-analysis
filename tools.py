# import yfinance as yf
# from crewai.tools import tool
# import pandas as pd
# import ta
# import numpy as np

# class StockAnalysisTools:
    
#     @tool("Fetch S&P 500 & Screen")
#     def fetch_and_screen_sp500():
#         """
#         Fetches the complete S&P 500 list, screens for the top 5 stocks based on 
#         recent trading volume and price momentum (technical strength), 
#         and returns their tickers.
#         """
#         try:
#             # Get S&P 500 tickers from Wikipedia
#             url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
#             tables = pd.read_html(url)
#             df = tables[0]
#             tickers = df['Symbol'].tolist()
            
#             # For demo speed, we'll take a random sample or top 20 to screen 
#             subset = tickers[:20] 
            
#             screened_results = []
            
#             for ticker in subset:
#                 try:
#                     stock = yf.Ticker(ticker)
#                     hist = stock.history(period="1mo")
#                     if hist.empty: continue
                    
#                     # Calculate simple momentum (Return)
#                     start_price = hist['Close'].iloc[0]
#                     end_price = hist['Close'].iloc[-1]
#                     momentum = ((end_price - start_price) / start_price) * 100
                    
#                     screened_results.append((ticker, momentum))
#                 except:
#                     continue
            
#             # Sort by momentum and take top 5
#             screened_results.sort(key=lambda x: x[1], reverse=True)
#             top_5 = [item[0] for item in screened_results[:5]]
            
#             return f"Top 5 Screened Stocks based on Momentum: {', '.join(top_5)}"
#         except Exception as e:
#             return "AAPL, NVDA, MSFT, AMD, TSLA"

#     @tool("Calculate Risk Metrics")
#     def calculate_risk_metrics(ticker: str):
#         """
#         Calculates detailed risk metrics: Beta, Volatility (Standard Deviation), 
#         and Maximum Drawdown for a specific stock.
#         """
#         try:
#             stock = yf.Ticker(ticker)
#             hist = stock.history(period="1y")
            
#             if hist.empty:
#                 return "No data found."
            
#             # Daily Returns
#             hist['pct_change'] = hist['Close'].pct_change()
            
#             # Volatility (Annualized Standard Deviation)
#             volatility = hist['pct_change'].std() * np.sqrt(252) * 100
            
#             # Max Drawdown
#             rolling_max = hist['Close'].cummax()
#             daily_drawdown = hist['Close'] / rolling_max - 1.0
#             max_drawdown = daily_drawdown.min() * 100
            
#             # Beta
#             beta = stock.info.get('beta', 'N/A')
            
#             return f"""
#             Risk Analysis for {ticker}:
#             - Beta: {beta} (Market Sensitivity)
#             - Annualized Volatility: {volatility:.2f}%
#             - Max Drawdown (1Y): {max_drawdown:.2f}%
#             """
#         except Exception as e:
#             return f"Error calculating risk for {ticker}: {e}"

#     @tool("Fetch Fundamental Data")
#     def fetch_fundamental_data(ticker: str):
#         """
#         Fetches fundamental data: P/E, Market Cap, EPS, and Sector.
#         """
#         try:
#             stock = yf.Ticker(ticker)
#             info = stock.info
#             simple_info = {
#                 "Ticker": ticker,
#                 "Price": info.get("currentPrice"),
#                 "MarketCap": info.get("marketCap"),
#                 "PE_Ratio": info.get("trailingPE"),
#                 "EPS": info.get("trailingEps"),
#                 "Sector": info.get("sector"),
#                 "TargetPrice": info.get("targetMeanPrice")
#             }
#             return str(simple_info)
#         except Exception as e:
#             return f"Error fetching fundamentals for {ticker}: {e}"

#     @tool("Calculate Technical Indicators")
#     def calculate_technicals(ticker: str):
#         """
#         Calculates RSI, MACD, and SMAs for a stock.
#         """
#         try:
#             stock = yf.Ticker(ticker)
#             df = stock.history(period="6mo")
#             if df.empty: return "No data."

#             # RSI
#             df['rsi'] = ta.momentum.RSIIndicator(df['Close']).rsi()
#             # MACD
#             macd = ta.trend.MACD(df['Close'])
#             df['macd'] = macd.macd()
#             df['macd_signal'] = macd.macd_signal()
#             # SMA
#             df['sma_50'] = ta.trend.SMAIndicator(df['Close'], window=50).sma_indicator()
#             df['sma_200'] = ta.trend.SMAIndicator(df['Close'], window=200).sma_indicator()
            
#             latest = df.iloc[-1]
#             return f"""
#             Technicals for {ticker}:
#             - Price: {latest['Close']:.2f}
#             - RSI: {latest['rsi']:.2f}
#             - MACD: {latest['macd']:.2f} (Signal: {latest['macd_signal']:.2f})
#             - SMA 50: {latest['sma_50']:.2f}
#             - SMA 200: {latest['sma_200']:.2f}
#             """
#         except Exception as e:
#             return f"Error with technicals for {ticker}: {e}"
import yfinance as yf
from crewai.tools import tool
import pandas as pd
import ta
import numpy as np
import requests
from langchain_community.tools import DuckDuckGoSearchRun

class StockAnalysisTools:
    
    # --- ALPHA VANTAGE TOOLS (High Value, Rate Limited) ---

    @tool("Fetch Market Movers")
    def fetch_market_movers(api_key: str):
        """
        Fetches the current Top Gainers, Losers, and Most Active stocks from the market.
        Useful for identifying trending stocks to analyze.
        """
        url = f"https://www.alphavantage.co/query?function=TOP_GAINERS_LOSERS&apikey={api_key}"
        try:
            response = requests.get(url)
            data = response.json()
            
            # Error Handling for Rate Limits
            if "Information" in data or "Note" in data:
                return "Error: Alpha Vantage Rate Limit Reached. Use fallback list."
            
            if "top_gainers" in data:
                # Get top 3 gainers to save context window
                gainers = data["top_gainers"][:3]
                result = [f"{g['ticker']} (+{g['change_percentage']})" for g in gainers]
                return ", ".join(result)
            return "No data found."
        except Exception as e:
            return f"API Error: {e}"

    @tool("Fetch News Sentiment")
    def fetch_news_sentiment(ticker: str, api_key: str):
        """
        Fetches comprehensive news sentiment and buzz scores for a stock using Alpha Vantage.
        Returns a summary of the market sentiment (Bullish/Bearish) and key news headlines.
        """
        url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={ticker}&sort=LATEST&limit=5&apikey={api_key}"
        try:
            response = requests.get(url)
            data = response.json()
            
            if "Information" in data or "Note" in data:
                return "Sentiment Data Unavailable (Rate Limit). Assume Neutral sentiment."
            
            if "feed" in data:
                articles = data["feed"]
                
                # Calculate aggregate sentiment score
                sentiment_scores = [float(a.get('overall_sentiment_score', 0)) for a in articles]
                avg_score = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
                
                # Interpret Score
                if avg_score >= 0.35: sentiment_label = "Bullish"
                elif avg_score <= -0.35: sentiment_label = "Bearish"
                else: sentiment_label = "Neutral"
                
                headlines = [f"- {a['title']} (Sentiment: {a['overall_sentiment_label']})" for a in articles[:3]]
                
                return f"""
                Sentiment Analysis for {ticker}:
                - Market Mood: {sentiment_label} (Score: {avg_score:.2f})
                - Recent Headlines:
                {chr(10).join(headlines)}
                """
            return "No news found."
        except Exception as e:
            return f"Sentiment Tool Error: {e}"

    # --- YFINANCE TOOLS (Unlimited, Reliable) ---

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
                "Sector": info.get("sector"),
                "Beta": info.get("beta")
            }
            return str(simple_info)
        except Exception as e:
            return f"Error fetching fundamentals: {e}"

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
            
            latest = df.iloc[-1]
            return f"""
            Technicals for {ticker}:
            - Price: {latest['Close']:.2f}
            - RSI: {latest['rsi']:.2f} (Over 70=Overbought, Under 30=Oversold)
            - MACD: {latest['macd']:.2f} (Signal: {latest['macd_signal']:.2f})
            - SMA 50: {latest['sma_50']:.2f}
            """
        except Exception as e:
            return f"Error with technicals: {e}"

    @tool("Calculate Risk Metrics")
    def calculate_risk_metrics(ticker: str):
        """
        Calculates detailed risk metrics: Beta, Volatility, and Max Drawdown.
        """
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1y")
            if hist.empty: return "No data."
            
            hist['pct_change'] = hist['Close'].pct_change()
            volatility = hist['pct_change'].std() * np.sqrt(252) * 100
            rolling_max = hist['Close'].cummax()
            daily_drawdown = hist['Close'] / rolling_max - 1.0
            max_drawdown = daily_drawdown.min() * 100
            
            return f"Risk: Volatility {volatility:.2f}%, Max Drawdown {max_drawdown:.2f}%"
        except Exception as e:
            return f"Risk Calc Error: {e}"