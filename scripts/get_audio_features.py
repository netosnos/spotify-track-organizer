#!/usr/bin/env python3
"""
Script to get audio features for tracks with RaccoonBeats IDs.
"""
import json
import requests
import time
from datetime import datetime, timedelta
from pathlib import Path

def format_time(seconds):
    """Format seconds into a human-readable time string"""
    return str(timedelta(seconds=int(seconds)))

def load_tracks_with_reccobeats() -> list:
    """Load tracks that have RaccoonBeats IDs from the fixed JSON file"""
    processed_dir = Path('data/processed')
    input_file = processed_dir / 'tracks_with_raccobeats_ids.json'
    
    if not input_file.exists():
        print("tracks_with_raccobeats_ids.json not found!")
        return []
    
    print(f"\nLoading tracks from: {input_file}")
    
    with open(input_file, 'r') as f:
        data = json.load(f)
        tracks = data.get('tracks', [])
    
    print(f"Found {len(tracks)} tracks with RaccoonBeats IDs")
    return tracks

def get_audio_features(tracks: list) -> tuple:
    """
    Get audio features for each track using RaccoonBeats IDs.
    
    Returns:
        tuple: (tracks_with_features, tracks_without_features)
    """
    base_url = "https://api.reccobeats.com"
    tracks_with_features = []
    tracks_without_features = []
    
    total_tracks = len(tracks)
    print(f"\nGetting audio features for {total_tracks} tracks...")
    
    # Track time for estimates
    start_time = time.time()
    last_update_time = start_time
    processed_count = 0
    
    for i, track in enumerate(tracks, 1):
        reccobeats_id = track['raccobeats_id']
        track_name = track['name']
        artists = track['artists']
        
        try:
            # Get audio features for this track
            features_url = f"{base_url}/v1/track/{reccobeats_id}/audio-features"
            
            # Calculate progress and time estimates
            current_time = time.time()
            elapsed_time = current_time - start_time
            processed_count += 1
            
            # Update progress every 5 tracks or when it's the last track
            if processed_count % 5 == 0 or i == total_tracks:
                time_per_track = elapsed_time / processed_count
                remaining_tracks = total_tracks - processed_count
                estimated_remaining_time = time_per_track * remaining_tracks
                
                print(f"\nProgress: {processed_count}/{total_tracks} tracks ({(processed_count/total_tracks)*100:.1f}%)")
                artist_names = [artist['name'] if isinstance(artist, dict) else artist for artist in artists]
                print(f"Current track: {track_name} by {', '.join(artist_names)}")
                print(f"Time elapsed: {format_time(elapsed_time)}")
                print(f"Estimated time remaining: {format_time(estimated_remaining_time)}")
                print(f"Average time per track: {time_per_track:.1f} seconds")
            
            response = requests.get(features_url)
            response.raise_for_status()
            
            # Add features to track info
            features = response.json()
            track['audio_features'] = features
            tracks_with_features.append(track)
            
            # Small delay to avoid rate limiting
            time.sleep(0.5)
            
        except requests.exceptions.RequestException as e:
            print(f"\nError getting features for {track_name}: {str(e)}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            tracks_without_features.append({
                'name': track_name,
                'artists': artists,
                'reccobeats_id': reccobeats_id,
                'error': str(e)
            })
    
    return tracks_with_features, tracks_without_features

def save_results(tracks_with_features: list, tracks_without_features: list):
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
            'total_tracks': len(tracks_with_features) + len(tracks_without_features),
            'tracks_with_features': len(tracks_with_features),
            'tracks_without_features': len(tracks_without_features)
        }
    }
    
    # Save tracks with features
    output_with_features = {
        **metadata,
        'tracks': tracks_with_features
    }
    with open(processed_dir / 'tracks_with_audio_features.json', 'w') as f:
        json.dump(output_with_features, f, indent=2)
    
    # Save tracks without features
    if tracks_without_features:
        output_without_features = {
            **metadata,
            'tracks': tracks_without_features
        }
        with open(processed_dir / 'tracks_without_audio_features.json', 'w') as f:
            json.dump(output_without_features, f, indent=2)
    
    print("\nResults saved to:")
    print(f"- {processed_dir / 'tracks_with_audio_features.json'}")
    if tracks_without_features:
        print(f"- {processed_dir / 'tracks_without_audio_features.json'}")

def main():
    start_time = time.time()
    
    # Load tracks with RaccoonBeats IDs
    tracks = load_tracks_with_reccobeats()
    
    if tracks:
        # Get audio features for these tracks
        tracks_with_features, tracks_without_features = get_audio_features(tracks)
        
        # Print summary
        total_time = time.time() - start_time
        print("\nSummary:")
        print(f"Total tracks processed: {len(tracks)}")
        print(f"Tracks with audio features: {len(tracks_with_features)}")
        print(f"Tracks without audio features: {len(tracks_without_features)}")
        print(f"Total processing time: {format_time(total_time)}")
        print(f"Average time per track: {total_time/len(tracks):.1f} seconds")
        
        if tracks_without_features:
            print("\nTracks without audio features:")
            for track in tracks_without_features[:5]:  # Show first 5 only
                artist_names = [artist['name'] if isinstance(artist, dict) else artist for artist in track['artists']]
                print(f"- {track['name']} by {', '.join(artist_names)}")
            if len(tracks_without_features) > 5:
                print(f"... and {len(tracks_without_features) - 5} more")
        
        # Save results
        save_results(tracks_with_features, tracks_without_features)
        
        # Print total execution time
        print(f"\nTotal execution time: {format_time(time.time() - start_time)}")
    else:
        print("No tracks with RaccoonBeats IDs found or error occurred")

if __name__ == "__main__":
    main() 