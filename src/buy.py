import pandas as pd
import numpy as np

def read_existing_portfolio(file_path):
    try:
        portfolio = pd.read_csv(file_path)
        return set(portfolio['Ticker'])
    except FileNotFoundError:
        print(f"Warning: Portfolio file '{file_path}' not found. Proceeding without portfolio weighting.")
        return set()

def read_sector_weights(file_path):
    try:
        weights_df = pd.read_csv(file_path, index_col='Sector')
        return weights_df.to_dict('index')
    except FileNotFoundError:
        print(f"Error: Sector weights file '{file_path}' not found. Cannot proceed.")
        raise

sector_weights = read_sector_weights('src/sector_weights.csv')

def score_stocks(df):
    """
    Score stocks based on various financial metrics, using raw values for P/E ratio and price change.
    Applies sector-specific scoring for all sectors and includes existing portfolio weighting.
    """
    # Read existing portfolio
    existing_portfolio = read_existing_portfolio('src/your_portfolio.csv')
    
    # Define the columns we'll use for scoring
    numerical_cols = ['Price Change (%)', 'Beta', 'P/E Ratio', 'Market Cap', 'Dividend Yield', 'RSI Score', 'Sector']
    
    # Remove stocks with any missing values in the relevant columns
    df_complete = df.dropna(subset=numerical_cols).copy()
    
    # Normalize numerical columns (except P/E Ratio and Price Change)
    for col in ['Beta', 'Market Cap', 'Dividend Yield', 'RSI Score']:
        df_complete[col] = pd.to_numeric(df_complete[col], errors='coerce')
        
        # Calculate min and max
        col_min = df_complete[col].min()
        col_max = df_complete[col].max()
        
        # Normalize the column, handling potential division by zero
        if col_max - col_min != 0:
            df_complete.loc[:, f'{col}_normalized'] = (df_complete[col] - col_min) / (col_max - col_min)
        else:
            df_complete.loc[:, f'{col}_normalized'] = 0.5  # Use 0.5 as a neutral value

    # Ensure P/E Ratio and Price Change are numeric
    df_complete['P/E Ratio'] = pd.to_numeric(df_complete['P/E Ratio'], errors='coerce')
    df_complete['Price Change (%)'] = pd.to_numeric(df_complete['Price Change (%)'], errors='coerce')

    # Apply sector-specific scoring and include portfolio weighting
    df_complete['score'] = df_complete.apply(lambda row: calculate_score(row, existing_portfolio), axis=1)
    
    return df_complete.sort_values('score', ascending=False)

def calculate_score(row, existing_portfolio):
    """Calculate the score for a single stock based on its sector and existing portfolio."""
    weights = sector_weights.get(row['Sector'], sector_weights['Other'])
    
    base_score = (
        row['Price Change (%)'] * weights['price_change'] +
        (1 - row['Beta_normalized']) * weights['beta'] +
        (20 / row['P/E Ratio']) * weights['pe_ratio'] +
        row['Market Cap_normalized'] * weights['market_cap'] +
        row['Dividend Yield_normalized'] * weights['dividend_yield'] +
        (0.5 - abs(row['RSI Score_normalized'] - 0.5)) * weights['rsi']
    )
    
    # Multiply score by 1.05 if the stock is in the existing portfolio
    portfolio_multiplier = 1.05 if row['Ticker'] in existing_portfolio else 1.0
    
    return base_score * portfolio_multiplier

def get_buy_recommendations(df, sector_counts):
    """
    Get top stock buy recommendations based on user-specified counts for each sector.
    """
    scored_df = score_stocks(df)
    
    recommendations = pd.DataFrame()

    for category, top_n in sector_counts.items():
        category_df = scored_df[scored_df['Sector'] == category]
        
        category_recommendations = category_df[
            (category_df['Beta'] < 1.5) &  # Filter out extremely volatile stocks
            (category_df['P/E Ratio'] > 0) &  # Filter out negative P/E ratios
            (category_df['RSI Score'] < 70)  # Avoid overbought stocks
        ].head(top_n)
        recommendations = pd.concat([recommendations, category_recommendations])

    return recommendations[['Ticker', 'Company', 'Sector', 'Current Close', 'Price Change (%)', 'P/E Ratio', 'Dividend Yield', 'RSI Score', 'score']]

def analyze_recommendations(df, sector_counts):
    """
    Provide a detailed analysis of the top stock recommendations for each specified sector.
    """
    recommendations = get_buy_recommendations(df, sector_counts)
    
    analysis = "Scoring Formulas for Each Sector:\n\n"
    for sector, weights in sector_weights.items():
        analysis += f"{sector} Sector:\n"
        analysis += f"Score = (Price Change (%) * {weights['price_change']:.2f}) + \n"
        analysis += f"        (Beta_normalized * {weights['beta']:.2f}) + \n"
        analysis += f"        ((20 / P/E Ratio) * {weights['pe_ratio']:.2f}) + \n"
        analysis += f"        (Market Cap_normalized * {weights['market_cap']:.2f}) + \n"
        analysis += f"        (Dividend Yield_normalized * {weights['dividend_yield']:.2f}) + \n"
        analysis += f"        ((0.5 - |RSI Score_normalized - 0.5|) * {weights['rsi']:.2f})\n\n"

    analysis += "Top Stock Recommendations by Sector:\n\n"
    
    for sector, count in sector_counts.items():
        sector_recommendations = recommendations[recommendations['Sector'] == sector]
        analysis += f"{sector} Sector Top {count} Stocks:\n"
        table = sector_recommendations.to_string(index=False)
        analysis += table + "\n\n"
    
    return analysis