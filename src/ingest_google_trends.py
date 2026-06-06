import os
import time
import logging
import pandas as pd
from pytrends.request import TrendReq

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

import json

# Load hairstyles list from configuration file
config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "hairstyles.json")
with open(config_path, "r", encoding="utf-8") as f:
    config_data = json.load(f)
hairstyles = config_data.get("hairstyles", [])

def fetch_google_trends():
    pytrends = TrendReq(hl='en-US', tz=360)
    
    merged_df = None

    logging.info("Starting Google Trends data ingestion...")

    for hair in hairstyles:
        logging.info(f"Fetching Google Trends data for: {hair}")
        
        success = False
        retries = 3
        while not success and retries > 0:
            try:
                # timeframe 'all' goes from 2004-01-01 to today on a monthly basis
                pytrends.build_payload([hair], cat=0, timeframe='all', geo='')
                data = pytrends.interest_over_time()
                
                if not data.empty:
                    # Drop the isPartial column if it exists
                    if 'isPartial' in data.columns:
                        data = data.drop(columns=['isPartial'])
                    
                    if merged_df is None:
                        merged_df = data
                    else:
                        # Join based on date index
                        merged_df = merged_df.join(data, how='outer')
                else:
                    logging.warning(f"No data found for {hair}")
                
                success = True
            except Exception as e:
                if '429' in str(e) or 'Rate' in str(e) or 'ResponseError' in str(type(e).__name__):
                    logging.error(f"Rate limit hit for {hair}. Retrying... Details: {e}")
                    time.sleep(10)
                    retries -= 1
                else:
                    logging.error(f"Unexpected error for {hair}: {e}")
                    break
        
        if not success:
            logging.error(f"Failed to fetch data for {hair} after retries.")
            
        time.sleep(3) # Delay to avoid rate limiting
        
    if merged_df is not None:
        # Reset index to make 'date' a column
        merged_df = merged_df.reset_index()
        merged_df = merged_df.fillna(0)
        
        filename = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "hairstyle_trends_google_trends_2004_today.csv")
        merged_df.to_csv(filename, index=False)
        logging.info(f"Done! Dataset saved as '{filename}'.")
    else:
        logging.warning("No data was collected from Google Trends.")

if __name__ == "__main__":
    fetch_google_trends()
