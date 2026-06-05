# WIP: Fashion Trend Analytics

## Table of Contents
- [Project Overview](#project-overview)
- [Data Sources](#data-sources)
- [Scripts](#scripts)
- [Automation](#automation)
- [Usage](#usage)

## Project Overview
This repository contains scripts to ingest music chart data and enrich it with artist genre information. The data pipeline downloads data from Kaggle, normalizes artist identifiers, and merges the datasets to provide genre classifications for Billboard Hot 100 entries.

## Data Sources
The project relies on two external datasets hosted on Kaggle:
- `ludmin/billboard`: Contains historical Billboard Hot 100 charts.
- `harshdprajapati/worldwide-music-artists-dataset-with-image`: Contains metadata for global music artists, including their associated genres.

## Scripts
The Python code is located in the `src/` directory.

- `ingest_data.py`: Authenticates with the Kaggle API using environment variables (`KAGGLE_USERNAME` and `KAGGLE_KEY`) and downloads the required datasets into the `data/` directory.
- `join_datasets.py`: Reads the downloaded CSV files, normalizes the artist names (e.g., lowercasing, removing punctuation, and extracting the primary artist from collaborative tracks), and performs a left join. The output is saved as `data/hot100_with_genre.csv`.

## Automation
A GitHub Actions workflow is defined in `.github/workflows/ingest_and_join.yml`. This workflow:
- Triggers on a weekly schedule (Sunday at midnight UTC) or manually via workflow dispatch.
- Sets up the environment and installs dependencies from `requirements.txt`.
- Executes the ingestion and join scripts.
- Commits the updated datasets back to the repository.

## Usage
To run the pipeline locally:

1. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set the Kaggle API credentials in a `.env` file at the root of the repository:
   ```env
   KAGGLE_USERNAME=your_username
   KAGGLE_KEY=your_api_key
   ```
3. Execute the ingestion script:
   ```bash
   python src/ingest_data.py
   ```
4. Execute the join script:
   ```bash
   python src/join_datasets.py
   ```
