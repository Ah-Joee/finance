import pandas as pd
import asyncio
import multiprocessing
import time
from src.stock_info import evaluate, mkdir
from src.buy import get_buy_recommendations, analyze_recommendations
from src.grok import grok
from src.query import query

async def main():
    print('\n<<< Stocks data fetching >>>')
    start_time = time.time()
    df = evaluate()
    end_time = time.time()
    print(f"Fetching time: {end_time - start_time}\n\n")

    print("\n<<< Sectors >>>\n")
    # Get user input for number of companies from each sector
    sectors = [
        'Basic Materials', 'Communication Services', 'Consumer Cyclical',
        'Consumer Defensive', 'Energy', 'Financial Services', 'Healthcare',
        'Industrials', 'Real Estate', 'Technology', 'Utilities', 'Other'
    ]
    sector_counts = {}
    for sector in sectors:
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
    
    today = pd.Timestamp('today').date()
    mkdir(f"analysis/{str(today)}")
    
    # Save all processed tickers
    all_tickers_file = f'analysis/{str(today)}/processed_tickers.csv'
    df.to_csv(all_tickers_file, index=False)

    # Save top stocks
    top_stocks_file = f'analysis/{str(today)}/top_stocks.csv'
    top_stocks.to_csv(top_stocks_file, index=False)

    # Display top stocks
    print("\n<<< Top Stocks to Consider >>>\n")
    print(top_stocks[['Company', 'Ticker', 'Sector', 'Current Close', 'Price Change (%)', 'P/E Ratio', 'Dividend Yield', 'RSI Score', 'score']])

    # Generate and save detailed analysis
    analysis = analyze_recommendations(df, sector_counts)
    with open(f'analysis/{str(today)}/analysis.md', "w", encoding='UTF-8') as analysis_file:
        analysis_file.write(analysis)

    q = query(sector_counts)
    response = '\n<<< Grok Analyzing >>>\n'
    response += await grok(q)
    with open(f'analysis/{str(today)}/analysis.md', "a", encoding='UTF-8') as grok_file:
        grok_file.write(response)
    print('\n')

if __name__ == '__main__':
    multiprocessing.freeze_support()  # This is necessary for Windows compatibility
    asyncio.run(main())