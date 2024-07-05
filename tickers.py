import yfinance as yf
import numpy as np
import pandas as pd
from tabulate import tabulate
import os
from concurrent.futures import ProcessPoolExecutor
import multiprocessing

# Set the number of cores to use
NUM_CORES = multiprocessing.cpu_count()

# Load stock info
stock_info = pd.read_csv('src/stock_info.csv')

def mkdir(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

def get_stock_data(ticker, period='5d'):
    try:
        data = yf.download(ticker, period=period)
        return ticker, data.reset_index()
    except Exception as e:
        print(f"Error downloading data for {ticker}: {e}")
        return ticker, None

def calculate_price_change(data):
    if len(data) < 2:
        return None
    current_price = data['Close'].iloc[-1]
    previous_close = data['Close'].iloc[-2]
    price_change = (current_price - previous_close) / previous_close * 100
    return round(price_change, 3)

def get_company_name(ticker):
    company_name = stock_info[stock_info['Ticker'] == ticker]['Name'].values
    return company_name[0] if len(company_name) > 0 else "Unknown"

def process_ticker(ticker, threshold, period='1mo'):
    ticker, data = get_stock_data(ticker, period)
    if data is None or data.empty:
        return None, ticker, None
    
    price_change = calculate_price_change(data)
    if price_change is None:
        return None, ticker, None
    
    current_date = data['Date'].iloc[-1]
    previous_price = data['Close'].iloc[-2]
    current_price = data['Close'].iloc[-1]
    company_name = get_company_name(ticker)
    
    result = [current_date, ticker, company_name, previous_price, current_price, price_change]
    return result, ticker, price_change

def process_chunk(chunk, threshold):
    return [process_ticker(ticker, threshold) for ticker in chunk]

def evaluate(threshold=0.5):

    all_tickers = stock_info['Ticker'].to_list()
    chunk_size = max(1, len(all_tickers) // NUM_CORES)
    chunks = [all_tickers[i:i + chunk_size] for i in range(0, len(all_tickers), chunk_size)]
    
    with ProcessPoolExecutor(max_workers=NUM_CORES) as executor:
        results = list(executor.map(process_chunk, chunks, [threshold] * len(chunks)))
    
    rising_stocks = []
    processed_tickers = []
    
    for chunk_result in results:
        for result, ticker, price_change in chunk_result:
            if ticker:
                processed_tickers.append((ticker, price_change))
            if result and price_change > threshold:
                rising_stocks.append(result)
    
    df = pd.DataFrame(rising_stocks, columns=["Date", "Ticker", "Company Name", "Previous Price", "Current Price", "Price Change (%)"])
    
    if not df.empty:
        table = tabulate(df, headers='keys', tablefmt='grid', floatfmt=".2f")
        print(table)
    else:
        print("No stocks met the rising threshold criteria.")
    
    # Save all processed tickers with their price changes
    processed_df = pd.DataFrame(processed_tickers, columns=["Ticker", "Price Change (%)"])
    processed_df.to_csv('src/processed_tickers.csv', index=False)
    
    return df

def main():
    threshold = float(input("How much rising in %? "))
    df = evaluate(threshold)
    today = pd.Timestamp('today').date()
    mkdir(f"{str(today)}")
    output_file = f'{str(today)}/{str(threshold)}_increase_stocks.csv'
    df.to_csv(output_file, index=False)
    print(f"Results saved to {output_file}")
    print(f"Total processed tickers: {len(pd.read_csv('src/processed_tickers.csv'))}")
    print(f"Tickers meeting threshold: {len(df)}")

if __name__ == '__main__':
    multiprocessing.freeze_support()  # This is necessary for Windows compatibility
    main()