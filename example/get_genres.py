#!/usr/bin/env python3

import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GenreAnalyzer:
    def __init__(self):
        try:
            # Initialize Spotify client with necessary scopes
            self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                client_id=os.getenv('SPOTIPY_CLIENT_ID'),
                client_secret=os.getenv('SPOTIPY_CLIENT_SECRET'),
                redirect_uri=os.getenv('SPOTIPY_REDIRECT_URI'),
                scope='user-library-read',
                open_browser=True
            ))
            
            # Get current user
            current_user = self.sp.current_user()
            self.user_id = current_user['id']
            print(f"\nConnected as: {current_user['display_name']}")
            
        except Exception as e:
            print(f"\nError connecting to Spotify: {str(e)}")
            raise

    def get_artist_genres(self, artist_id):
        """Get genres for a specific artist"""
        try:
            artist = self.sp.artist(artist_id)
            return artist['genres']
        except Exception as e:
            print(f"Error getting genres for artist {artist_id}: {str(e)}")
            return []

    def list_unique_genres(self):
        """List all unique genres from liked songs"""
        try:
            print("\nFetching your liked songs...")
            offset = 0
            limit = 50
            unique_genres = set()
            total_songs = 0
            
            # Get all liked songs
            while True:
                results = self.sp.current_user_saved_tracks(limit=limit, offset=offset)
                if not results['items']:
                    break
                
                for item in results['items']:
                    track = item['track']
                    artist_id = track['artists'][0]['id']
                    
                    # Get genres for the artist
                    genres = self.get_artist_genres(artist_id)
                    unique_genres.update(genres)
                    
                    total_songs += 1
                    print(f"\rAnalyzing songs... {total_songs} songs processed", end="", flush=True)
                
                offset += limit
                if not results['next']:
                    break
            
            print(f"\n\nAnalyzed {total_songs} songs in total")
            
            # Print all unique genres
            print("\nAll unique genres in your library:")
            for genre in sorted(unique_genres):
                print(f"- {genre}")
            
        except Exception as e:
            print(f"\nError listing genres: {str(e)}")
            raise

def main():
    try:
        analyzer = GenreAnalyzer()
        analyzer.list_unique_genres()
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        print("\nPlease try again or check your credentials.")

if __name__ == "__main__":
    main() 