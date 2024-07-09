import os, multiprocessing, logging
import yfinance as yf
import pandas as pd
from concurrent.futures import ProcessPoolExecutor

# Suppress the error message from yfinance in case the ticker is not available
logger = logging.getLogger('yfinance')
logger.disabled = True
logger.propagate = False

# Set the number of cores to use
NUM_CORES = multiprocessing.cpu_count() * 4

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

def calculate_rsi(data, period=14):
    """
    Calculate the Relative Strength Index (RSI) for a given set of price data.

    Args:
        data (pd.DataFrame): A DataFrame containing the 'Close' column with price data.
        period (int): The number of periods to use for the RSI calculation.

    Returns:
        float: The RSI value.
    """
    delta = data['Close'].diff(1)
    up = delta.copy()
    down = delta.copy()
    up[up < 0] = 0
    down[down > 0] = 0
    avg_gain = up.ewm(com=period-1, adjust=False).mean()
    avg_loss = down.ewm(com=period-1, adjust=False).mean().abs()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

def calculate_macd(data):
    """
    Calculate the Moving Average Convergence Divergence (MACD) for a given set of price data.

    Args:
        data (pd.DataFrame): A DataFrame containing the 'Close' column with price data.

    Returns:
        tuple: The MACD, MACD signal line, and MACD histogram values.
    """
    exp1 = data['Close'].ewm(span=12, adjust=False).mean()
    exp2 = data['Close'].ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd.iloc[-1], signal.iloc[-1], macd.iloc[-1] - signal.iloc[-1]

def process_ticker(ticker):
    """
    Process a single stock ticker and calculate the required metrics.

    Args:
        ticker (str): The stock ticker.

    Returns:
        tuple: A tuple containing the calculated metrics, the ticker, and the price change percentage.
    """
    try:
        ticker_info = yf.Ticker(ticker).info
        if 'currentPrice' not in ticker_info or 'previousClose' not in ticker_info:
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
        rsi_score = calculate_rsi(pd.DataFrame({'Close': [current_price]}))
        macd, macd_signal, macd_hist = calculate_macd(pd.DataFrame({'Close': [current_price]}))

        result = [company_name, ticker, sector, current_price, open_price, previous_close, price_change, beta, pe_ratio, market_cap, fifty_two_week_high, fifty_two_week_low, dividend_yield, avg_volume, rsi_score, macd, macd_signal, macd_hist]
        return result, ticker, price_change
    except Exception:
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
            if ticker and price_change is not None:
                processed_tickers.append(result)
    
    # Save all processed tickers with their metrics
    columns = ["Company", "Ticker", "Sector", "Current Close", "Open", "Previous Close", "Price Change (%)", "Beta", "P/E Ratio", "Market Cap", "52-Week High", "52-Week Low", "Dividend Yield", "Average Volume", "RSI Score", "MACD", "MACD Signal", "MACD Hist"]    
    processed_df = pd.DataFrame(processed_tickers, columns=columns)

    return processed_df
