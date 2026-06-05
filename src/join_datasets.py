import pandas as pd
from pathlib import Path
import re

def clean_artist_name(name):
    if not isinstance(name, str):
        return ""
    # Lowercase
    name = name.lower()
    
    # Split by common multi-artist separators and take the first one
    pattern = r'(?i)( feat\. | ft\. | featuring | & | x | and | / |, |\+ )'
    parts = re.split(pattern, name)
    primary_artist = parts[0]
    
    # Remove any extra spaces or special characters at the end
    primary_artist = primary_artist.strip()
    
    # Remove some punctuation that might mess up matches
    primary_artist = primary_artist.replace('"', '').replace("'", "")
    
    return primary_artist

def main():
    repo_root = Path(__file__).resolve().parent.parent
    data_dir = repo_root / "data"
    
    hot100_path = data_dir / "hot100.csv"
    artists_path = data_dir / "Global Music Artists.csv"
    output_path = data_dir / "hot100_with_genre.csv"
    
    if not hot100_path.exists() or not artists_path.exists():
        print("Required datasets not found in the data directory. Please run ingest_data.py first.")
        return
    
    print("Reading datasets...")
    # Read datasets. Explicitly specify encoding to prevent issues on some systems.
    hot100_df = pd.read_csv(hot100_path, encoding='utf-8')
    artists_df = pd.read_csv(artists_path, encoding='utf-8')
    
    print("Cleaning artist names...")
    # Clean Hot 100 artist names
    hot100_df['cleaned_artist'] = hot100_df['Artist'].apply(clean_artist_name)
    
    # Clean Global Music Artists names
    artists_df['cleaned_artist'] = artists_df['artist_name'].apply(clean_artist_name)
    
    # Drop duplicates in artists dataset on cleaned_artist to avoid creating duplicates in Hot 100
    artists_unique = artists_df.drop_duplicates(subset=['cleaned_artist'], keep='first')
    
    # Select columns to merge
    artists_subset = artists_unique[['cleaned_artist', 'artist_genre', 'artist_img', 'country']]
    
    print("Joining datasets...")
    joined_df = pd.merge(hot100_df, artists_subset, on='cleaned_artist', how='left')
    
    # Drop the temporary column used for joining
    joined_df.drop(columns=['cleaned_artist'], inplace=True)
    
    print(f"Writing joined dataset to {output_path}...")
    joined_df.to_csv(output_path, index=False)
    
    # Let's print out some stats
    total_records = len(joined_df)
    matched_records = joined_df['artist_genre'].notna().sum()
    print(f"Join complete! {matched_records} out of {total_records} records matched ({matched_records/total_records:.2%}).")

if __name__ == "__main__":
    main()
