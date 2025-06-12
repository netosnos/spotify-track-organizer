#!/usr/bin/env python3
"""
Script to get RaccoonBeats IDs for Spotify liked songs.
"""
import json
import requests
import time
from datetime import datetime
from pathlib import Path

def load_spotify_songs(file_path: str) -> list:
    """Load Spotify songs from JSON file"""
    with open(file_path, 'r') as f:
        return json.load(f)

def get_reccobeats_info(spotify_tracks: list) -> tuple:
    """
    Get RaccoonBeats IDs for Spotify tracks.
    
    Returns:
        tuple: (tracks_with_ids, tracks_without_ids)
    """
    base_url = "https://api.reccobeats.com"
    tracks_with_ids = []
    tracks_without_ids = []
    
    # Process tracks in batches of 40
    batch_size = 40
    total_batches = (len(spotify_tracks) + batch_size - 1) // batch_size
    
    print(f"\nProcessing {len(spotify_tracks)} tracks in {total_batches} batches...")
    
    for i in range(0, len(spotify_tracks), batch_size):
        batch = spotify_tracks[i:i + batch_size]
        spotify_ids = [track['id'] for track in batch]
        current_batch = (i // batch_size) + 1
        
        try:
            # Get track information
            track_url = f"{base_url}/v1/track"
            params = {
                'ids': ','.join(spotify_ids)
            }
            print(f"\rProcessing batch {current_batch}/{total_batches} ({(current_batch/total_batches)*100:.1f}%)", end='')
            
            response = requests.get(track_url, params=params)
            response.raise_for_status()
            
            # Parse the response
            content = response.json()
            tracks = content.get('content', [])
            
            # Check which tracks don't have RaccoonBeats IDs
            received_ids = {track.get('href', '').split('/')[-1] for track in tracks if track.get('href')}
            for track in batch:
                if track['id'] not in received_ids:
                    tracks_without_ids.append({
                        'name': track['name'],
                        'artists': track['artists'],
                        'spotify_id': track['id']
                    })
                else:
                    # Find the matching RaccoonBeats track
                    racco_track = next((t for t in tracks if t.get('href', '').split('/')[-1] == track['id']), None)
                    if racco_track:
                        track_with_id = track.copy()
                        track_with_id['raccobeats_id'] = racco_track.get('id')
                        tracks_with_ids.append(track_with_id)
            
            # Small delay to avoid rate limiting
            time.sleep(0.5)
            
        except requests.exceptions.RequestException as e:
            print(f"\nError processing batch {current_batch}: {str(e)}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
    
    return tracks_with_ids, tracks_without_ids

def save_results(tracks_with_ids: list, tracks_without_ids: list):
    """Save results to JSON files"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Create data directory if it doesn't exist
    Path('data/processed').mkdir(parents=True, exist_ok=True)
    
    # Save tracks with RaccoonBeats IDs
    with open(f'data/processed/tracks_with_raccobeats_{timestamp}.json', 'w') as f:
        json.dump(tracks_with_ids, f, indent=2)
    
    # Save tracks without RaccoonBeats IDs
    if tracks_without_ids:
        with open(f'data/processed/tracks_without_raccobeats_{timestamp}.json', 'w') as f:
            json.dump(tracks_without_ids, f, indent=2)
    
    print(f"\nResults saved with timestamp: {timestamp}")

def main():
    # Find the most recent liked songs file
    raw_dir = Path('data/raw')
    liked_songs_files = list(raw_dir.glob('liked_songs_*.json'))
    
    if not liked_songs_files:
        print("No liked songs file found in data/raw directory")
        return
    
    # Get the most recent file
    latest_file = max(liked_songs_files, key=lambda x: x.stat().st_mtime)
    print(f"Using file: {latest_file}")
    
    # Load Spotify songs
    spotify_tracks = load_spotify_songs(latest_file)
    print(f"Loaded {len(spotify_tracks)} tracks from Spotify")
    
    # Get RaccoonBeats IDs
    tracks_with_ids, tracks_without_ids = get_reccobeats_info(spotify_tracks)
    
    # Print summary
    print("\n\nSummary:")
    print(f"Total tracks processed: {len(spotify_tracks)}")
    print(f"Tracks with RaccoonBeats IDs: {len(tracks_with_ids)}")
    print(f"Tracks without RaccoonBeats IDs: {len(tracks_without_ids)}")
    
    if tracks_without_ids:
        print("\nTracks without RaccoonBeats IDs:")
        for track in tracks_without_ids[:5]:  # Show first 5 only
            print(f"- {track['name']} by {', '.join(track['artists'])}")
        if len(tracks_without_ids) > 5:
            print(f"... and {len(tracks_without_ids) - 5} more")
    
    # Save results
    save_results(tracks_with_ids, tracks_without_ids)

if __name__ == "__main__":
    main() 