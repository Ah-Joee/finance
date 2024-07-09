import os, multiprocessing, logging
import yfinance as yf
import pandas as pd
import numpy as np
from concurrent.futures import ProcessPoolExecutor

# Suppress the error message from yfinance in case the ticker is not available
logger = logging.getLogger('yfinance')
logger.disabled = True
logger.propagate = False

# Set the number of cores to use
NUM_CORES = multiprocessing.cpu_count() * 2

# Load stock info
stock_info = pd.read_csv('src/stock_info.csv')

def mkdir(directory_path):
    """
    Create a directory if it doesn't exist.

    Args:
        directory_path (str): The path of the directory to create.
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

def get_company_name(ticker):
    """
    Get the company name for a given stock ticker.

    Args:
        ticker (str): The stock ticker.

    Returns:
        str: The company name, or "Unknown" if not found.
    """
    company_name = stock_info[stock_info['Ticker'] == ticker]['Name'].values
    return company_name[0] if len(company_name) > 0 else "Unknown"

def calculate_price_change(current_price, previous_close):
    """
    Calculate the percentage change in price between the current price and the previous close.

    Args:
        current_price (float): The current price of the stock.
        previous_close (float): The previous close price of the stock.

    Returns:
        float: The percentage change in price, or None if the previous close is 0.
    """
    if previous_close == 0:
        return None
    price_change = (current_price - previous_close) / previous_close * 100
    return round(price_change, 3)

def calculate_rsi(data, periods=14):
    """
    Calculate the Relative Strength Index (RSI) for a given set of price data.

    Args:
        data (pd.Series): A Series containing the closing prices.
        periods (int): The number of periods to use for RSI calculation (default is 14).

    Returns:
        float: The RSI value for the most recent period.
    """
    delta = data.diff()

    # Make two series: one for lower closes and one for higher closes
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    
    # Calculate the EWMA
    ma_up = up.ewm(com = periods - 1, adjust=False).mean()
    ma_down = down.ewm(com = periods - 1, adjust=False).mean()

    rsi = ma_up / ma_down
    rsi = 100 - (100/(1 + rsi))

    return rsi.iloc[-1]

def process_ticker(ticker):
    """
    Process a single stock ticker and calculate the required metrics.

    Args:
        ticker (str): The stock ticker.

    Returns:
        tuple: A tuple containing the calculated metrics, the ticker, and the price change percentage.
    """
    try:
        stock = yf.Ticker(ticker)
        ticker_info = stock.info
        if 'currentPrice' not in ticker_info or 'previousClose' not in ticker_info:
            return None, ticker, None

        # Fetch historical data for RSI calculation
        hist_data = stock.history(period="1mo")
        if len(hist_data) < 14:  # We need at least 14 days of data for RSI
            return None, ticker, None

        company_name = get_company_name(ticker)
        current_price = ticker_info['currentPrice']
        previous_close = ticker_info['previousClose']
        open_price = ticker_info['open']
        beta = ticker_info.get('beta', None)
        pe_ratio = ticker_info.get('trailingPE', None)
        market_cap = ticker_info.get('marketCap', None)
        sector = ticker_info.get('sector', None)
        fifty_two_week_high = ticker_info.get('fiftyTwoWeekHigh', None)
        fifty_two_week_low = ticker_info.get('fiftyTwoWeekLow', None)
        dividend_yield = ticker_info.get('dividendYield', None)
        avg_volume = ticker_info.get('averageVolume', None)

        price_change = calculate_price_change(current_price, previous_close)
        rsi_score = calculate_rsi(hist_data['Close'])

        result = [company_name, ticker, sector, current_price, open_price, previous_close, price_change, beta, pe_ratio, market_cap, fifty_two_week_high, fifty_two_week_low, dividend_yield, avg_volume, rsi_score]
        return result, ticker, price_change
    except Exception as e:
        return None, ticker, None

def process_chunk(chunk):
    """
    Process a chunk of stock tickers in parallel.

    Args:
        chunk (list): A list of stock tickers to process.

    Returns:
        list: A list of results for the processed tickers.
    """
    return [process_ticker(ticker) for ticker in chunk]

def evaluate():
    """
    Evaluate the stock data for the given tickers and return a DataFrame with the calculated metrics.

    Returns:
        pd.DataFrame: A DataFrame containing the calculated metrics for each stock ticker.
    """
    all_tickers = stock_info['Ticker'].to_list()
    chunk_size = max(1, len(all_tickers) // NUM_CORES)
    chunks = [all_tickers[i:i + chunk_size] for i in range(0, len(all_tickers), chunk_size)]
    
    with ProcessPoolExecutor(max_workers=NUM_CORES) as executor:
        results = list(executor.map(process_chunk, chunks))
    
    processed_tickers = []
    
    for chunk_result in results:
        for result, ticker, price_change in chunk_result:
            if result is not None:
                processed_tickers.append(result)
    
    # Save all processed tickers with their metrics
    columns = ["Company", "Ticker", "Sector", "Current Close", "Open", "Previous Close", "Price Change (%)", "Beta", "P/E Ratio", "Market Cap", "52-Week High", "52-Week Low", "Dividend Yield", "Average Volume", "RSI Score"]    
    processed_df = pd.DataFrame(processed_tickers, columns=columns)

    return processed_df