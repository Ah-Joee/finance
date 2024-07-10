import pandas as pd

def query(sector_counts):
    today = pd.Timestamp('today').date()
    q = "Put all the companies in a number list. Within each one, write a summary why they are good targets to buy using only the data provided below."
    q += '\n\n```Data'
    
    with open(f'analysis/{str(today)}/top_stocks.csv', 'r') as f:
        s = '\n' + f.read()
    q += s

    q += '```\n'

    q += 'The score is calculated as follows: \n'
    q += "Score = (Price Change (%) * sector_weight['price_change']) + \n"
    q += "        (Beta_normalized * sector_weight['beta']) + \n"
    q += "        ((15 / P/E Ratio) * sector_weight['pe_ratio']) + \n"
    q += "        (Market Cap_normalized * sector_weight['market_cap']) + \n"
    q += "        (Dividend Yield_normalized * sector_weight['dividend_yield']) + \n"
    q += "        ((1 - |RSI Score_normalized - 0.7|) * sector_weight['rsi'])\n\n"

    q += "Number of companies selected from each sector:\n"
    for sector, count in sector_counts.items():
        q += f"{sector}: {count}\n"

    with open(f'analysis/{str(today)}/analysis.txt', "w", encoding='UTF-8') as my_output_file:
        my_output_file.write(q)
    return q
