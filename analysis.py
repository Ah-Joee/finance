import asyncio
import pandas as pd
from src.query import query
from src.grok import grok
from src.buy import get_buy_recommendations, analyze_recommendations



async def main():
    today = pd.Timestamp('today').date()

    df = pd.read_csv(f"analysis/{str(today)}/processed_tickers.csv")

    print("<<< # from each Sectors >>>\n")
    # Get user input for number of companies from each sector
    sector_counts = {}
    for sector in ['Technology', 'Consumer Cyclical', 'Financial Services', 'Other']:
        while True:
            try:
                count = int(input(f"How many companies do you want from the {sector} sector? "))
                if count < 0:
                    print("Please enter a non-negative integer.")
                else:
                    sector_counts[sector] = count
                    break
            except ValueError:
                print("Please enter a valid integer.")

    # Get top recommendations
    top_stocks = get_buy_recommendations(df, sector_counts)
    

    # Save top stocks
    top_stocks_file = f'analysis/{str(today)}/top_stocks.csv'
    top_stocks.to_csv(top_stocks_file, index=False)

    # Display top stocks
    print("\n<<< Top Stocks to Consider >>>\n")
    print(top_stocks[['Company', 'Ticker', 'Sector', 'Current Close', 'Price Change (%)', 'P/E Ratio', 'Dividend Yield', 'RSI Score', 'score']])

    # Generate and save detailed analysis
    analysis = analyze_recommendations(df, sector_counts)
    with open(f'analysis/{str(today)}/detailed_analysis.txt', "w", encoding='UTF-8') as analysis_file:
        analysis_file.write(analysis)

    q = query(sector_counts)
    response = '\n<<< Grok Analyzing >>>\n'
    response += await grok(q)
    with open(f'analysis/{str(today)}/grok_analysis.txt', "a", encoding='UTF-8') as grok_file:
        grok_file.write(response)
    print('\n')

if __name__ == '__main__':
    asyncio.run(main())
