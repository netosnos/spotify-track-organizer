#!/usr/bin/env python3
"""
Test file to analyze unique genres from tracks with audio features.
"""
import json
from pathlib import Path
from collections import Counter
from datetime import datetime

def load_audio_features():
    """Load tracks with audio features from JSON file"""
    file_path = Path('data/processed/tracks_with_audio_features.json')
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, 'r') as f:
        data = json.load(f)
        return data.get('tracks', [])

def get_unique_genres(tracks):
    """Get unique genres from all tracks"""
    all_genres = []
    for track in tracks:
        for artist in track['artists']:
            all_genres.extend(artist.get('genres', []))
    
    # Count occurrences of each genre
    genre_counter = Counter(all_genres)
    
    # Sort genres by frequency (most common first)
    sorted_genres = sorted(genre_counter.items(), key=lambda x: (-x[1], x[0]))
    
    return sorted_genres

def save_analysis_to_file(genre_stats, total_genres, output_file):
    """Save genre analysis to a text file"""
    with open(output_file, 'w') as f:
        f.write("Genre Analysis Report\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("Genre Statistics:\n")
        f.write("-" * 50 + "\n")
        f.write(f"{'Genre':<30} {'Count':<10} {'Percentage':<10}\n")
        f.write("-" * 50 + "\n")
        
        for genre, count in genre_stats:
            percentage = (count / total_genres) * 100
            f.write(f"{genre:<30} {count:<10} {percentage:.1f}%\n")
        
        f.write("\nSummary:\n")
        f.write(f"Total unique genres: {len(genre_stats)}\n")
        f.write(f"Total genre occurrences: {total_genres}\n")

def main():
    try:
        # Load tracks
        tracks = load_audio_features()
        print(f"\nAnalyzing genres from {len(tracks)} tracks...")
        
        # Get unique genres
        genre_stats = get_unique_genres(tracks)
        
        # Calculate total genres
        total_genres = sum(count for _, count in genre_stats)
        
        # Save analysis to file
        output_file = Path('tests/genre_analysis.txt')
        save_analysis_to_file(genre_stats, total_genres, output_file)
        
        # Print results to console
        print("\nGenre Statistics:")
        print("-" * 50)
        print(f"{'Genre':<30} {'Count':<10} {'Percentage':<10}")
        print("-" * 50)
        
        for genre, count in genre_stats:
            percentage = (count / total_genres) * 100
            print(f"{genre:<30} {count:<10} {percentage:.1f}%")
        
        print("\nSummary:")
        print(f"Total unique genres: {len(genre_stats)}")
        print(f"Total genre occurrences: {total_genres}")
        print(f"\nAnalysis saved to: {output_file}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 