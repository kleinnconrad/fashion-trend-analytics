import os
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def get_monthly_genre_prevalence(df):
    """Calculates the monthly prevalence of each genre in the Hot 100."""
    df['YearMonth'] = pd.to_datetime(df['hot100_Date']).dt.to_period('M')
    
    df_genres = df.dropna(subset=['hot100_artist_genre']).copy()
    # Split the comma-separated genres
    df_genres['genre'] = df_genres['hot100_artist_genre'].str.split(', ')
    df_exploded = df_genres.explode('genre')
    
    # Count genres per month
    monthly_counts = df_exploded.groupby(['YearMonth', 'genre']).size().reset_index(name='count')
    total_per_month = df_exploded.groupby('YearMonth').size().reset_index(name='total')
    
    monthly_counts = pd.merge(monthly_counts, total_per_month, on='YearMonth')
    monthly_counts['prevalence'] = monthly_counts['count'] / monthly_counts['total']
    
    return monthly_counts

def create_correlation_heatmap(df, output_dir):
    """Creates a heatmap correlating top genres with hairstyles."""
    logging.info("Generating correlation heatmap...")
    
    monthly_genres = get_monthly_genre_prevalence(df)
    
    # Find the top 20 genres overall
    top_genres = monthly_genres.groupby('genre')['count'].sum().nlargest(20).index
    monthly_genres_top = monthly_genres[monthly_genres['genre'].isin(top_genres)]
    
    # Pivot to get a time-series of genres
    genre_pivot = monthly_genres_top.pivot(index='YearMonth', columns='genre', values='prevalence').fillna(0)
    
    # Extract Google Trends hairstyle data (it's monthly, so we can just drop duplicates per month)
    gtrends_cols = [c for c in df.columns if c.startswith('gtrends_')]
    df_hairstyles = df[['YearMonth'] + gtrends_cols].drop_duplicates('YearMonth').set_index('YearMonth')
    
    # Merge both time-series
    merged_ts = pd.concat([genre_pivot, df_hairstyles], axis=1).dropna()
    
    # Calculate correlation between genres and hairstyles
    full_corr = merged_ts.corr()
    genre_hair_corr = full_corr.loc[top_genres, gtrends_cols]
    
    # Clean up column names for the plot
    genre_hair_corr.columns = [c.replace('gtrends_', '') for c in genre_hair_corr.columns]
    
    plt.figure(figsize=(16, 10))
    sns.heatmap(genre_hair_corr, cmap='coolwarm', center=0, annot=False)
    plt.title('Correlation between Top 20 Music Genres and Hairstyle Popularity (2004-Today)')
    plt.ylabel('Music Genre (Hot 100)')
    plt.xlabel('Hairstyle (Google Trends)')
    
    plt.tight_layout()
    out_path = os.path.join(output_dir, 'correlation_heatmap.png')
    plt.savefig(out_path, dpi=300)
    plt.close()
    logging.info(f"Saved correlation heatmap to {out_path}")

def create_interactive_timeline(df, output_dir):
    """Creates an interactive timeline with dropdowns for all hairstyles and top 20 genres."""
    logging.info("Generating fully interactive timeline with dropdowns...")
    
    monthly_genres = get_monthly_genre_prevalence(df)
    top_genres = monthly_genres.groupby('genre')['count'].sum().nlargest(20).index.tolist()
    
    gtrends_cols = [c for c in df.columns if c.startswith('gtrends_')]
    df_hair = df[['YearMonth'] + gtrends_cols].drop_duplicates('YearMonth').sort_values('YearMonth')
    df_hair['Date'] = df_hair['YearMonth'].dt.to_timestamp()
    
    # Pivot genres
    monthly_genres_top = monthly_genres[monthly_genres['genre'].isin(top_genres)]
    genre_pivot = monthly_genres_top.pivot(index='YearMonth', columns='genre', values='prevalence').fillna(0).reset_index()
    genre_pivot['Date'] = genre_pivot['YearMonth'].dt.to_timestamp()
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Traces 0 to 31: Hairstyles
    for i, col in enumerate(gtrends_cols):
        hair_name = col.replace('gtrends_', '').title()
        fig.add_trace(
            go.Scatter(
                x=df_hair['Date'], 
                y=df_hair[col], 
                name=hair_name + " Search Interest", 
                line=dict(width=3),
                visible=(i == 0) # Only first is visible initially
            ),
            secondary_y=False,
        )
        
    # Traces 32 to 51: Genres
    for i, genre in enumerate(top_genres):
        fig.add_trace(
            go.Scatter(
                x=genre_pivot['Date'], 
                y=genre_pivot[genre], 
                name=genre.title() + " Chart Prevalence", 
                line=dict(width=2, dash='dot'),
                visible=(i == 0) # Only first is visible initially
            ),
            secondary_y=True,
        )
        
    # Create Hairstyle Dropdown
    hair_buttons = []
    for i, col in enumerate(gtrends_cols):
        visible_array = [False] * len(gtrends_cols)
        visible_array[i] = True
        hair_name = col.replace('gtrends_', '').title()
        hair_buttons.append(dict(
            label=hair_name,
            method="restyle",
            args=[{"visible": visible_array}, list(range(len(gtrends_cols)))],
        ))
        
    # Create Genre Dropdown
    genre_buttons = []
    for i, genre in enumerate(top_genres):
        visible_array = [False] * len(top_genres)
        visible_array[i] = True
        genre_buttons.append(dict(
            label=genre.title(),
            method="restyle",
            args=[{"visible": visible_array}, list(range(len(gtrends_cols), len(gtrends_cols) + len(top_genres)))],
        ))
        
    fig.update_layout(
        title_text="Temporal Alignment: Hairstyle vs. Music Genre",
        hovermode="x unified",
        template='plotly_white',
        updatemenus=[
            dict(
                active=0,
                buttons=hair_buttons,
                x=0.1,
                xanchor="left",
                y=1.15,
                yanchor="top",
                direction="down",
                showactive=True,
            ),
            dict(
                active=0,
                buttons=genre_buttons,
                x=0.45,
                xanchor="left",
                y=1.15,
                yanchor="top",
                direction="down",
                showactive=True,
            )
        ]
    )
    
    # Add annotations for dropdowns
    fig.update_layout(
        annotations=[
            dict(text="Hairstyle:", x=0.01, xref="paper", y=1.12, yref="paper", align="left", showarrow=False),
            dict(text="Music Genre:", x=0.36, xref="paper", y=1.12, yref="paper", align="left", showarrow=False)
        ]
    )
    
    fig.update_yaxes(title_text="Google Trends Search Interest (0-100)", secondary_y=False)
    fig.update_yaxes(title_text="Genre Prevalence in Hot 100", secondary_y=True)
    
    out_path = os.path.join(output_dir, 'interactive_timeline.html')
    fig.write_html(out_path)
    logging.info(f"Saved interactive timeline to {out_path}")

def main():
    parser = argparse.ArgumentParser(description="Visualize Fashion and Music Trends")
    args = parser.parse_args()
    
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(root_dir, "data", "final_joined_dataset.csv")
    output_dir = os.path.join(root_dir, "output")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    logging.info(f"Loading {data_path}...")
    df = pd.read_csv(data_path)
    
    create_correlation_heatmap(df, output_dir)
    create_interactive_timeline(df, output_dir)
    
    logging.info("All visualizations generated successfully.")

if __name__ == "__main__":
    main()
