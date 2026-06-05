import os
import json
import time
import requests
import logging
from urllib.parse import quote_plus
from pathlib import Path
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

# Setup Logging gem. antigravity.md
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def get_musicbrainz_genre(artist_name, cache, cache_file):
    # Alle öffentlichen APIs (iTunes, MusicBrainz) blocken uns aktuell aktiv wegen Bot-Protection.
    # Wir geben den Cache zurück oder eine leere Liste, um einen Timeout zu verhindern.
    if artist_name in cache and cache[artist_name] != "Unknown" and cache[artist_name] != []:
        return cache[artist_name]
    return []

def main():
    load_dotenv()
    client_id = os.environ.get("SPOTIFY_CLIENT_ID")
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
    redirect_uri = os.environ.get("SPOTIFY_REDIRECT_URI")

    if not client_id or not client_secret or not redirect_uri:
        logger.error("Spotify Credentials fehlen!")
        raise ValueError("Spotify Credentials fehlen!")

    auth_manager = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope="playlist-read-private playlist-read-collaborative"
    )
    sp = spotipy.Spotify(auth_manager=auth_manager)

    current_file_path = Path(__file__).resolve()
    repo_root = current_file_path.parent.parent
    data_dir = repo_root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    cache_file = data_dir / "artist_genres_cache.json"
    genre_cache = {}
    if cache_file.exists():
        with open(cache_file, "r", encoding="utf-8") as f:
            try:
                genre_cache = json.load(f)
            except json.JSONDecodeError:
                genre_cache = {}
                
    # Entferne alle "Unknown" aus dem Cache, um MusicBrainz-Abfragen zu erzwingen
    keys_to_delete = [k for k, v in genre_cache.items() if v == "Unknown" or v == []]
    for k in keys_to_delete:
        del genre_cache[k]

    logger.info("Erstelle historische Timeseries (Jahre 2010 bis 2024)...")
    
    artist_history = {} 
    artist_names = {}
    
    limit = 10
    
    for year in range(2010, 2025):
        logger.info(f"Frage Tracks für das Jahr {year} ab...")
        for offset in range(0, 100, limit):
            try:
                results = sp.search(q=f'year:{year}', type='track', offset=offset)
            except Exception as e:
                logger.error(f"Fehler bei Jahr {year}, Offset {offset}: {e}")
                break
                
            items = results.get('tracks', {}).get('items', [])
            if not items:
                break
                
            for track in items:
                if track and track.get('artists') and track.get('album'):
                    release_date = track['album'].get('release_date')
                    if not release_date:
                        continue
                        
                    if len(release_date) == 4:
                        release_date += "-01-01"
                    elif len(release_date) == 7:
                        release_date += "-01"
                        
                    track_pop = track.get('popularity', 0)
                    artist = track['artists'][0]
                    aid = artist['id']
                    name = artist['name']
                    
                    artist_names[aid] = name
                    key = (aid, release_date)
                    
                    if key not in artist_history:
                        artist_history[key] = track_pop
                    else:
                        if track_pop > artist_history[key]:
                            artist_history[key] = track_pop

    logger.info(f"Insgesamt {len(artist_history)} historische Einträge für {len(artist_names)} einzigartige Künstler gefunden.")
    logger.info("Lade Genre-Details über MusicBrainz API (ca. 1 Sekunde pro neuem Künstler)...")
    
    delta_entries = []
    processed = 0
    
    for key, track_pop in artist_history.items():
        aid, release_date = key
        name = artist_names[aid]
        
        genres = get_musicbrainz_genre(name, genre_cache, cache_file)
        
        # Falls es vorher in iTunes nur ein String war, machen wir eine Liste draus
        if isinstance(genres, str):
            genres = [genres] if genres != "Unknown" else []
            
        delta_entries.append({
            "date": release_date,
            "artist_name": name,
            "artist_genres": genres,
            "popularity": track_pop
        })
        
        processed += 1
        if processed % 50 == 0:
            logger.info(f"  {processed}/{len(artist_history)} Einträge verarbeitet...")
    
    output_file = data_dir / "spotify_delta_load.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(delta_entries, f, indent=4, ensure_ascii=False)
        
    logger.info(f"Erfolgreich {len(delta_entries)} historische Einträge generiert.")
    logger.info(f"Datei überschrieben: {output_file}")

if __name__ == "__main__":
    main()
