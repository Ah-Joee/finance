import pandas as pd

def score_stocks(df):
    # Normalize numerical columns
    numerical_cols = ['Price Change (%)', 'Beta', 'P/E Ratio', 'Market Cap', 'Dividend Yield', 'RSI Score']
    for col in numerical_cols:
        # Convert column to numeric, replacing non-numeric values with NaN
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Calculate min and max, ignoring NaN values
        col_min = df[col].min()
        col_max = df[col].max()
        
        # Normalize the column, handling potential division by zero
        if col_max - col_min != 0:
            df[f'{col}_normalized'] = (df[col] - col_min) / (col_max - col_min)
        else:
            df[f'{col}_normalized'] = 0  # or any other default value

    # Create a composite score
    df['score'] = (
        df['Price Change (%)_normalized'].fillna(0) * 0.2 +
        df['Beta_normalized'].fillna(0) * 0.1 +
        (1 - df['P/E Ratio_normalized'].fillna(1)) * 0.2 +
        df['Market Cap_normalized'].fillna(0) * 0.1 +
        df['Dividend Yield_normalized'].fillna(0) * 0.2 +
        (1 - df['RSI Score_normalized'].fillna(1)) * 0.2
    )
    
    return df.sort_values('score', ascending=False)