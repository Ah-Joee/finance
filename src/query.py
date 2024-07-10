import pandas as pd

def query(sector_counts):
    today = pd.Timestamp('today').date()
    q = '```Data'
    
    with open(f'analysis/{str(today)}/top_stocks.csv', 'r') as f:
        s = '\n' + f.read()
    q += s
    q += '```\n'
    q += "Write the analysis for each of the companies provided in the Data section. " 
    q += "Make sure all the companies have their own section of analysis.\n"

    for sector, count in sector_counts.items():
        q += f"{sector}: {count}\n"

    with open(f'analysis/{str(today)}/analysis.md', "w", encoding='UTF-8') as my_output_file:
        my_output_file.write(q)
    return q
