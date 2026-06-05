import os
import json
from datetime import datetime
from pathlib import Path
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

def main():
    # 1. Credentials aus den Umgebungsvariablen laden
    client_id = os.environ.get("SPOTIFY_CLIENT_ID")
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise ValueError("Spotify Credentials fehlen! Bitte SPOTIFY_CLIENT_ID und SPOTIFY_CLIENT_SECRET setzen.")

    # 2. Spotify API authentifizieren
    auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(auth_manager=auth_manager)

    # Offizielle "Top 50 - Global" Playlist ID
    PLAYLIST_ID = "37i9dQZEVXbMDoHDwVN2tF" 
    print("Lade Tracks aus der Top 50 Global Playlist...")
    
    results = sp.playlist_tracks(PLAYLIST_ID)
    
    # 3. Einzigartige Künstler-IDs extrahieren
    artist_ids = set()
    for item in results['items']:
        track = item.get('track')
        if track and track.get('artists'):
            # Wir fokussieren uns auf den Hauptkünstler des Tracks
            artist_ids.add(track['artists'][0]['id'])
            
    print(f"{len(artist_ids)} einzigartige Künstler gefunden. Lade Genre-Details...")
    
    # 4. Künstler-Details abfragen (max. 50 auf einmal, was hier perfekt passt)
    artist_ids_list = list(artist_ids)
    artists_data = sp.artists(artist_ids_list)['artists']
    
    current_date = datetime.now().strftime("%Y-%m-%d")
    delta_entries = []
    
    for artist in artists_data:
        delta_entries.append({
            "date": current_date,
            "artist_name": artist['name'],
            "artist_genres": artist['genres'], # In JSON bleibt das eine saubere Liste!
            "popularity": artist['popularity']
        })
        
    # 5. Pfad-Logik für src -> data
    # __file__ zeigt auf dieses Skript im src-Ordner. parent.parent ist das Hauptverzeichnis.
    current_file_path = Path(__file__).resolve()
    repo_root = current_file_path.parent.parent
    data_dir = repo_root / "data"
    
    # Ordner erstellen, falls er noch nicht existiert
    data_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = data_dir / "spotify_delta_load.json"
    
    # 6. JSON Append-Logik (Bestehende Daten laden und neue anhängen)
    existing_data = []
    if output_file.exists():
        with open(output_file, "r", encoding="utf-8") as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                # Falls die Datei existiert, aber leer/fehlerhaft ist
                existing_data = []
                
    existing_data.extend(delta_entries)
    
    # 7. Datei schreiben
    with open(output_file, "w", encoding="utf-8") as f:
        # ensure_ascii=False sorgt dafür, dass Umlaute oder Sonderzeichen korrekt gespeichert werden
        json.dump(existing_data, f, indent=4, ensure_ascii=False)
        
    print(f"Erfolgreich {len(delta_entries)} Einträge generiert.")
    print(f"Datei aktualisiert: {output_file}")

if __name__ == "__main__":
    main()
