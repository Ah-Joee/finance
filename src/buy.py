import pandas as pd
import numpy as np

def score_stocks(df):
    """
    Score stocks based on various financial metrics.

    This function normalizes several key financial indicators and combines them
    into a single composite score. Higher scores indicate potentially more
    attractive stocks based on the given criteria.

    Args:
        df (pd.DataFrame): DataFrame containing stock data with required columns.

    Returns:
        pd.DataFrame: The input DataFrame with additional columns for normalized
                      metrics and a composite score, sorted by score in descending order.
    """
    # Define the columns we'll use for scoring
    numerical_cols = ['Price Change (%)', 'Beta', 'P/E Ratio', 'Market Cap', 'Dividend Yield', 'RSI Score']
    
    # Normalize numerical columns
    for col in numerical_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Calculate min and max, ignoring NaN values
        col_min = df[col].min()
        col_max = df[col].max()
        
        # Normalize the column, handling potential division by zero
        if col_max - col_min != 0:
            df[f'{col}_normalized'] = (df[col] - col_min) / (col_max - col_min)
        else:
            df[f'{col}_normalized'] = 0.5  # Use 0.5 as a neutral value

    # Create a composite score with adjusted weights and logic
    df['score'] = (
        df['Price Change (%)_normalized'].fillna(0) * 0.15 +  # Recent performance
        (1 - df['Beta_normalized'].fillna(0.5)) * 0.1 +       # Lower beta is better
        (1 - df['P/E Ratio_normalized'].fillna(1)) * 0.25 +   # Lower P/E is better
        df['Market Cap_normalized'].fillna(0) * 0.1 +         # Larger companies
        df['Dividend Yield_normalized'].fillna(0) * 0.2 +     # Higher dividend yield
        (df['RSI Score_normalized'].fillna(0.5) - 0.5).abs() * -0.2  # Prefer RSI closer to 50
    )
    
    return df.sort_values('score', ascending=False)

def get_buy_recommendations(df, top_n=10):
    """
    Get top stock buy recommendations based on composite scores and additional filters.

    This function applies the scoring system and then filters the results to
    exclude highly volatile stocks, stocks with negative P/E ratios, and
    overbought stocks based on RSI.

    Args:
        df (pd.DataFrame): DataFrame containing stock data.
        top_n (int): Number of top recommendations to return. Default is 10.

    Returns:
        pd.DataFrame: A DataFrame containing the top N recommended stocks
                      with key metrics and scores.
    """
    scored_df = score_stocks(df)
    
    # Add some additional filters
    recommendations = scored_df[
        (scored_df['Beta'] < 1.5) &  # Filter out extremely volatile stocks
        (scored_df['P/E Ratio'] > 0) &  # Filter out negative P/E ratios
        (scored_df['RSI Score'] < 70)  # Avoid overbought stocks
    ].head(top_n)
    
    return recommendations[['Ticker', 'Company', 'Current Close', 'Price Change (%)', 'P/E Ratio', 'Dividend Yield', 'RSI Score', 'score']]

def analyze_recommendations(df):
    """
    Provide a detailed analysis of the top stock recommendations.

    This function generates a formatted string containing an analysis of each
    recommended stock, including key metrics and additional insights based on
    P/E ratio and RSI values.

    Args:
        df (pd.DataFrame): DataFrame containing stock data.

    Returns:
        str: A formatted string containing the analysis of top stock recommendations.
    """
    recommendations = get_buy_recommendations(df)
    
    analysis = f"Top {len(recommendations)} Stock Recommendations:\n\n"
    
    for _, stock in recommendations.iterrows():
        analysis += f"{stock['Ticker']} - {stock['Company']}:\n"
        analysis += f"  Current Price: ${stock['Current Close']:.2f}\n"
        analysis += f"  Price Change: {stock['Price Change (%)']:.2f}%\n"
        analysis += f"  P/E Ratio: {stock['P/E Ratio']:.2f}\n"
        analysis += f"  Dividend Yield: {stock['Dividend Yield']*100:.2f}%\n"
        analysis += f"  RSI: {stock['RSI Score']:.2f}\n"
        analysis += f"  Score: {stock['score']:.4f}\n\n"
        
        if stock['RSI Score'] < 30:
            analysis += "  Note: This stock may be oversold based on its low RSI.\n"
        elif stock['RSI Score'] > 60:
            analysis += "  Note: This stock is approaching overbought territory.\n"
        
        if stock['P/E Ratio'] < 15:
            analysis += "  Note: This stock has a relatively low P/E ratio, which could indicate it's undervalued.\n"
        
        analysis += "\n"
    
    return analysis
