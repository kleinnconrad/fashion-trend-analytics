# Data Directory Overview

## Table of Contents
- [Raw Data](#raw-data)
- [Processed Data](#processed-data)

This directory contains the raw and processed datasets used in the Fashion Trend Analytics project.

## Raw Data
* `hot100.csv`: The historical Billboard Hot 100 charts, downloaded from Kaggle.
* `Global Music Artists.csv`: Metadata for global music artists, including their associated genres, downloaded from Kaggle.

## Processed Data
* `hot100_with_genre.csv`: The intermediate dataset created by joining `hot100.csv` with `Global Music Artists.csv` on the normalized artist names.
* `hairstyle_trends_complete_1950_2019.csv`: Yearly frequency data for curated hairstyles from 1950 to 2019, fetched from the Google Books Ngram Corpus. Values are scaled up by 1e9 for readability.
* `hairstyle_trends_google_trends_2004_today.csv`: Monthly relative search interest data for curated hairstyles from 2004 to the present, fetched from Google Trends. Values range from 0 to 100.
* `final_joined_dataset.csv`: The ultimate dataset combining the Hot 100 chart data with the Ngram and Google Trends hairstyle data. Columns are prefixed with `hot100_`, `ngram_`, and `gtrends_` to indicate their origin.
