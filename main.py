import pandas as pd
import multiprocessing
from src.stock_info_extract import evaluate, mkdir



def main():
    df = evaluate()
    today = pd.Timestamp('today').date()
    mkdir(f"{str(today)}")
    output_file = f'{str(today)}/processed_tickers.csv'
    df.to_csv(output_file, index=False)


if __name__ == '__main__':
    multiprocessing.freeze_support()  # This is necessary for Windows compatibility
    main()