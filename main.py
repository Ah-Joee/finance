import pandas as pd
import asyncio
import multiprocessing
from src.stock_info_extract import evaluate, mkdir
from src.buy import score_stocks
from src.grok import grok
from src.query import query



async def main():
    df = evaluate()
    
    # Score and rank stocks
    df_scored = score_stocks(df)
    
    # Select top 10 stocks
    top_10_stocks = df_scored.head(10)
    
    today = pd.Timestamp('today').date()
    mkdir(f"{str(today)}")
    
    # Save all processed tickers
    all_tickers_file = f'{str(today)}/processed_tickers.csv'
    df.to_csv(all_tickers_file, index=False)
    print(f"All processed tickers saved to {all_tickers_file}")
    
    # Save top 10 stocks
    top_10_file = f'{str(today)}/top_10_stocks.csv'
    top_10_stocks.to_csv(top_10_file, index=False)
    print(f"Top 10 stocks saved to {top_10_file}")
    
    # Display top 10 stocks
    print("\nTop 10 Stocks to Consider:")
    print(top_10_stocks[['Company', 'Ticker', 'Current Close', 'Price Change (%)', 'P/E Ratio', 'Dividend Yield', 'RSI Score', 'score']])

    q = query()
    response = '\n<<< Grok >>>\n'
    response += await grok(q)
    with open(f'{str(today)}/analysis.txt', "a", encoding='UTF-8') as my_output_file:
        my_output_file.write(response)
    print(response)

if __name__ == '__main__':
    multiprocessing.freeze_support()  # This is necessary for Windows compatibility
    asyncio.run(main())