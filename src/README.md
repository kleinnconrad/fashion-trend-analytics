# Source Code Directory Overview

## Table of Contents
- [Data Ingestion Scripts](#data-ingestion-scripts)
- [Data Transformation Scripts](#data-transformation-scripts)

This directory contains the Python scripts used for data ingestion and transformation in the Fashion Trend Analytics project.

## Data Ingestion Scripts
* `ingest_data.py`: Connects to the Kaggle API using environment variables to download the raw Billboard Hot 100 and Global Music Artists datasets.
* `ingest_hairstyles.py`: Iterates through the list of hairstyles in `config/hairstyles.json` and fetches historical yearly frequencies from the Google Books Ngram API (1950 to 2019).
* `ingest_google_trends.py`: Iterates through the list of hairstyles in `config/hairstyles.json` and fetches monthly relative search volumes using the Google Trends API (from 2004 to today).

## Data Transformation Scripts
* `join_datasets.py`: Cleans and normalizes artist names, and performs a join between the Billboard Hot 100 chart data and the global artists dataset to append genres to the chart entries.
* `join_all_datasets.py`: Reads the Hot 100 dataset, the Google Ngram dataset, and the Google Trends dataset, prefixes their columns to mark their origin, and performs a series of left joins based on the appropriate timeframes (Year and Year-Month) to produce the final comprehensive dataset.
