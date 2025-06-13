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
        data = json.load(f)
        return data.get('data', [])

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
    """Save results to JSON files with metadata"""
    # Create data directory if it doesn't exist
    processed_dir = Path('data/processed')
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    # Prepare metadata
    current_time = datetime.now().isoformat()
    metadata = {
        'metadata': {
            'created_at': current_time,
            'updated_at': current_time,
            'total_tracks': len(tracks_with_ids) + len(tracks_without_ids),
            'tracks_with_ids': len(tracks_with_ids),
            'tracks_without_ids': len(tracks_without_ids)
        }
    }
    
    # Save tracks with RaccoonBeats IDs
    output_with_ids = {
        **metadata,
        'tracks': tracks_with_ids
    }
    with open(processed_dir / 'tracks_with_raccobeats_ids.json', 'w') as f:
        json.dump(output_with_ids, f, indent=2)
    
    # Save tracks without RaccoonBeats IDs
    if tracks_without_ids:
        output_without_ids = {
            **metadata,
            'tracks': tracks_without_ids
        }
        with open(processed_dir / 'tracks_without_raccobeats_ids.json', 'w') as f:
            json.dump(output_without_ids, f, indent=2)
    
    print("\nResults saved to:")
    print(f"- {processed_dir / 'tracks_with_raccobeats_ids.json'}")
    if tracks_without_ids:
        print(f"- {processed_dir / 'tracks_without_raccobeats_ids.json'}")

def main():
    # Use the liked_songs.json file from raw folder
    liked_songs_file = Path('data/raw/liked_songs.json')
    
    if not liked_songs_file.exists():
        print("liked_songs.json not found in data/raw directory")
        return
    
    print(f"Using file: {liked_songs_file}")
    
    # Load Spotify songs
    spotify_tracks = load_spotify_songs(liked_songs_file)
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