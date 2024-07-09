import pandas as pd

def query():
    today = pd.Timestamp('today').date()
    q = 'The provided data is the ten recommended buy stocks. '
    q += 'Explain to me why they are good targets to buy. Explain one by one and use only the provided data.'  
    q += '\n```Data'
    
    with open(f'{str(today)}/top_10_stocks.csv', 'r') as f:
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

    with open(f'{str(today)}/analysis.txt', "w", encoding='UTF-8') as my_output_file:
        my_output_file.write(q)
    return q