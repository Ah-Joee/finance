import pandas as pd
import asyncio
import multiprocessing
from src.stock_info import evaluate, mkdir
from src.buy import score_stocks
from src.grok import grok
from src.query import query



async def main():
    print('\n<<< Stocks data fetching >>>\n')
    df = evaluate()
    
    print('<<< Customized score calculating >>>\n')
    # Score and rank stocks
    df_scored = score_stocks(df)
    
    print("<<< Choosing top 10 stocks >>>\n")
    # Select top 10 stocks
    top_10_stocks = df_scored.head(10)
    
    today = pd.Timestamp('today').date()
    mkdir(f"analysis/{str(today)}")
    
    # Save all processed tickers
    all_tickers_file = f'analysis/{str(today)}/processed_tickers.csv'
    df.to_csv(all_tickers_file, index=False)

    
    # Save top 10 stocks
    top_10_file = f'analysis/{str(today)}/top_10_stocks.csv'
    top_10_stocks.to_csv(top_10_file, index=False)

    
    # Display top 10 stocks
    print("<<< Top 10 Stocks to Consider >>>\n")
    print(top_10_stocks[['Company', 'Ticker', 'Current Close', 'Price Change (%)', 'P/E Ratio', 'Dividend Yield', 'RSI Score', 'score']])

    q = query()
    response = '\n<<< Grok Analyzing >>>\n'
    response += await grok(q)
    with open(f'analysis/{str(today)}/analysis.txt', "a", encoding='UTF-8') as my_output_file:
        my_output_file.write(response)
    print('\n')

if __name__ == '__main__':
    multiprocessing.freeze_support()  # This is necessary for Windows compatibility
    asyncio.run(main())