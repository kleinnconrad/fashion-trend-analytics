import os
import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def join_datasets():
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    
    hot100_path = os.path.join(data_dir, "hot100_with_genre.csv")
    ngram_path = os.path.join(data_dir, "hairstyle_trends_complete_1950_2019.csv")
    gtrends_path = os.path.join(data_dir, "hairstyle_trends_google_trends_2004_today.csv")
    
    logging.info("Loading datasets...")
    df_hot100 = pd.read_csv(hot100_path)
    df_ngram = pd.read_csv(ngram_path)
    df_gtrends = pd.read_csv(gtrends_path)
    
    # Prefix columns with origin
    df_hot100 = df_hot100.add_prefix('hot100_')
    df_ngram = df_ngram.add_prefix('ngram_')
    df_gtrends = df_gtrends.add_prefix('gtrends_')
    
    # To facilitate the join, we extract Year and Year-Month from hot100_Date
    # Hot100 date format is YYYY-MM-DD
    df_hot100['join_year'] = df_hot100['hot100_Date'].str[0:4]
    df_hot100['join_year_month'] = df_hot100['hot100_Date'].str[0:7]
    
    # Make sure ngram year is a string for joining
    df_ngram['ngram_Year'] = df_ngram['ngram_Year'].astype(str)
    
    # Google Trends date format is YYYY-MM-01, we extract YYYY-MM
    df_gtrends['join_year_month'] = df_gtrends['gtrends_date'].str[0:7]
    
    logging.info("Joining datasets...")
    
    # Left outer join with ngram on Year
    joined_df = pd.merge(df_hot100, df_ngram, left_on='join_year', right_on='ngram_Year', how='left')
    
    # Left outer join with gtrends on Year-Month
    joined_df = pd.merge(joined_df, df_gtrends, on='join_year_month', how='left')
    
    # Keep only the hot100_Date column among date columns, and drop the temporary join columns
    cols_to_drop = ['join_year', 'join_year_month', 'ngram_Year', 'gtrends_date']
    joined_df = joined_df.drop(columns=[col for col in cols_to_drop if col in joined_df.columns])
    
    out_path = os.path.join(data_dir, "final_joined_dataset.csv")
    joined_df.to_csv(out_path, index=False)
    
    logging.info(f"Done! Final joined dataset saved to {out_path}")

if __name__ == "__main__":
    join_datasets()
