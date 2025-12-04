import requests
import pandas as pd

# ---------------------------------------------------------
# 🔑 PASTE YOUR ALPHA VANTAGE API KEY HERE
# Get one for free at: https://www.alphavantage.co/support/#api-key
API_KEY = "3YG17HDDK9OBPHU4"
# ---------------------------------------------------------

def get_market_movers(api_key):
    """
    Fetches Top Gainers, Losers, and Most Active stocks from Alpha Vantage.
    """
    # if api_key ==:
    #     print("❌ Error: You must replace 'YOUR_API_KEY_HERE' with a valid key.")
    #     return

    url = f"https://www.alphavantage.co/query?function=TOP_GAINERS_LOSERS&apikey={api_key}"
    
    print("📡 Connecting to Alpha Vantage API...")
    try:
        response = requests.get(url)
        data = response.json()

        # Check for API errors (e.g., limit reached or invalid key)
        if "Information" in data:
            print(f"⚠️ API Limit Reached: {data['Information']}")
            return
        if "Error Message" in data:
            print("❌ Invalid API Key or Endpoint.")
            return

        # extract Top Gainers
        if "top_gainers" in data:
            gainers = data["top_gainers"]
            
            # Convert to DataFrame for nice display
            df = pd.DataFrame(gainers)
            
            # Clean up column names/types
            df.rename(columns={
                "ticker": "Ticker",
                "price": "Price",
                "change_amount": "Change $",
                "change_percentage": "Change %",
                "volume": "Volume"
            }, inplace=True)
            
            # Select top 5
            top_5 = df.head(5)
            
            print("\n🏆 Top 5 Market Gainers (Real-Time):")
            print("-" * 50)
            # Print row by row for clarity
            for index, row in top_5.iterrows():
                print(f"🟢 {row['Ticker']:<6} | Price: ${row['Price']:<8} | Change: {row['Change %']}")
            print("-" * 50)
            
            return [stock['Ticker'] for stock in gainers[:5]]
            
        else:
            print("❌ No 'top_gainers' data found in response.")
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    # Run the fetcher
    tickers = get_market_movers(API_KEY)
    
    if tickers:
        print(f"\n✅ Tickers ready for AI Analysis: {', '.join(tickers)}")