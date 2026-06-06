import urllib.request
import json
import pandas as pd
import time
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Load hairstyles list from configuration file
config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "hairstyles.json")
with open(config_path, "r", encoding="utf-8") as f:
    config_data = json.load(f)
hairstyles = config_data.get("hairstyles", [])

year_start = 1950
year_end = 2019 # Hard limit of Google Ngram Corpus 26

df = pd.DataFrame({'Year': range(year_start, year_end + 1)})

logging.info("Downloading data from Google Ngram...")

for hair in hairstyles:
    logging.info(f"Querying: {hair}")
    query = hair.replace(' ', '+')
    
    url = f"https://books.google.com/ngrams/json?content={query}&year_start={year_start}&year_end={year_end}&corpus=26&smoothing=0"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            
            if data:
                timeseries = data[0]['timeseries']
                
                if len(timeseries) == len(df):
                    # Scale values by 1e9 to make the dataset easier to read and analyze
                    scaled_timeseries = [val * 1e9 for val in timeseries]
                    df[hair] = scaled_timeseries
                else:
                    logging.warning(f"Data length mismatch for {hair}.")
            else:
                logging.warning(f"No data found for {hair}")
                
    except Exception as e:
        logging.error(f"Error with {hair}: {e}")
    
    time.sleep(1) # Protection against API rate limits

df = df.fillna(0)

filename = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "hairstyle_trends_complete_1950_2019.csv")
df.to_csv(filename, index=False)
logging.info(f"Done! Dataset saved as '{filename}'.")