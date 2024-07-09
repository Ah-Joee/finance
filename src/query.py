import pandas as pd

def query():
    today = pd.Timestamp('today').date()
    q = "For each of the ten companies, use the provided data, summarize why each of them are a good target to buy. "
    q += "Incorporate the metrics, tell me in details why they got recommended."
    q += '\n```Data'
    
    with open(f'analysis/{str(today)}/top_10_stocks.csv', 'r') as f:
        s = '\n' + f.read()
    q += s

    q += '```\n'

    q += 'The score is calculated as follows: \n'
    q += "'Price Change (%)_normalized' * 0.2 + \
        'Beta_normalized' * 0.1 + \
        (1 - 'P/E Ratio_normalized') * 0.2 + \
        'Market Cap_normalized' * 0.1 + \
        'Dividend Yield_normalized' * 0.2 + \
        (1 - 'RSI Score_normalized') * 0.2 \n"

    with open(f'analysis/{str(today)}/analysis.txt', "w", encoding='UTF-8') as my_output_file:
        my_output_file.write(q)
    return q