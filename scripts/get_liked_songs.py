#!/usr/bin/env python3
"""
Script to fetch and save Spotify liked songs.
"""
import json
import os
from datetime import datetime
from src.spotify.liked_songs import get_all_liked_songs, extract_song_details

def save_songs_to_json(songs: list, filename: str):
    """
    Save songs data to a JSON file.
    
    Args:
        songs (list): List of songs to save
        filename (str): Name of the file to save to
    """
    # Create data/raw directory if it doesn't exist
    os.makedirs('data/raw', exist_ok=True)
    
    # Save to file
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(songs, f, indent=2, ensure_ascii=False)

def main():
    """Main function to fetch and save liked songs."""
    print("Fetching liked songs from Spotify...")
    
    # Get all liked songs
    raw_songs = get_all_liked_songs()
    print(f"Found {len(raw_songs)} liked songs")
    
    # Extract relevant details
    songs = [extract_song_details(song) for song in raw_songs]
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'data/raw/liked_songs_{timestamp}.json'
    
    # Save to file
    save_songs_to_json(songs, filename)
    print(f"Saved {len(songs)} songs to {filename}")

if __name__ == '__main__':
    main() 