"""
Spotify API client implementation.
Handles authentication and provides methods to interact with the Spotify Web API.
"""
import os
import time
import requests
from typing import Optional, Dict, Any, List
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

class SpotifyClient:
    def __init__(self):
        """Initialize the Spotify client with authentication."""
        load_dotenv()
        
        # Get credentials from environment variables
        self.client_id = os.getenv('SPOTIPY_CLIENT_ID')
        self.client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')
        self.redirect_uri = os.getenv('SPOTIPY_REDIRECT_URI')
        
        if not all([self.client_id, self.client_secret, self.redirect_uri]):
            raise ValueError("Missing required Spotify credentials in environment variables")
        
        # Initialize the Spotify client with necessary scopes
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            scope='user-library-read'  # Scope for reading user's liked songs
        ))
    
    def get_liked_songs(self, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """
        Get user's liked songs from Spotify.
        
        Args:
            limit (int): Maximum number of songs to return (default: 50)
            offset (int): Offset for pagination (default: 0)
            
        Returns:
            Dict[str, Any]: Dictionary containing the liked songs data
        """
        try:
            return self.sp.current_user_saved_tracks(limit=limit, offset=offset)
        except Exception as e:
            raise Exception(f"Error fetching liked songs: {str(e)}")
    
    def get_all_liked_songs(self) -> list:
        """
        Get all user's liked songs by handling pagination automatically.
        
        Returns:
            list: List of all liked songs
        """
        all_songs = []
        offset = 0
        limit = 50  # Maximum allowed by Spotify API
        
        print("\nFetching liked songs from Spotify...")
        print(f"Using batch size of {limit} songs per request")
        
        while True:
            print(f"\nFetching songs {offset} to {offset + limit}...")
            results = self.get_liked_songs(limit=limit, offset=offset)
            if not results['items']:
                print("No more songs found.")
                break
                
            all_songs.extend(results['items'])
            print(f"Retrieved {len(results['items'])} songs")
            offset += limit
            
            # If we got less than the limit, we've reached the end
            if len(results['items']) < limit:
                print("Reached end of liked songs.")
                break
        
        print(f"\nTotal songs retrieved: {len(all_songs)}")
        return all_songs

    def get_artists_genres(self, artist_ids: List[str]) -> Dict[str, List[str]]:
        """
        Get genres for multiple artists using batch processing.
        
        Args:
            artist_ids (List[str]): List of artist IDs to fetch genres for
            
        Returns:
            Dict[str, List[str]]: Dictionary mapping artist IDs to their genres
        """
        if not artist_ids:
            print("No artist IDs provided.")
            return {}
            
        # Remove duplicates while preserving order
        unique_ids = list(dict.fromkeys(artist_ids))
        genres_by_artist = {}
        
        print(f"\nProcessing {len(unique_ids)} unique artists...")
        
        # Get the access token for direct API calls
        print("Getting access token...")
        token = self.sp._auth_manager.get_access_token()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        print("Access token obtained successfully.")
        
        # Process in batches of 50 (Spotify's maximum for the batch endpoint)
        batch_size = 50
        total_batches = (len(unique_ids) + batch_size - 1) // batch_size
        
        print(f"\nStarting genre fetching for {len(unique_ids)} artists in {total_batches} batches")
        print("Using batch size of 50 artists per request (Spotify's maximum)")
        print("Adding 5 second delay between batches to avoid rate limits")
        
        # Statistics tracking
        artists_with_genres = 0
        artists_without_genres = 0
        
        for i in range(0, len(unique_ids), batch_size):
            batch = unique_ids[i:i + batch_size]
            current_batch = (i // batch_size) + 1
            
            print(f"\n{'='*50}")
            print(f"Processing batch {current_batch}/{total_batches}")
            print(f"Artists in this batch: {len(batch)}")
            print(f"Progress: {i}/{len(unique_ids)} artists processed")
            print(f"{'='*50}")
            
            # Add a delay between batches to avoid rate limits
            if i > 0:
                wait_time = 5  # 5 second delay between batches
                print(f"\nWaiting {wait_time} seconds before next batch...")
                time.sleep(wait_time)
            
            try:
                # Make direct API call to the batch endpoint
                print("\nMaking API request...")
                response = requests.get(
                    f'https://api.spotify.com/v1/artists?ids={",".join(batch)}',
                    headers=headers
                )
                
                if response.status_code == 429:  # Rate limit exceeded
                    retry_after = int(response.headers.get('Retry-After', 1))
                    print(f"\nRate limit exceeded. Waiting {retry_after} seconds...")
                    time.sleep(retry_after)
                    # Retry this batch
                    i -= batch_size
                    continue
                
                response.raise_for_status()
                artists_data = response.json()
                
                # Process the batch of artists
                print("\nProcessing artist data...")
                for artist in artists_data['artists']:
                    if artist:  # Some artists might be None if not found
                        genres = artist.get('genres', [])
                        genres_by_artist[artist['id']] = genres
                        if genres:
                            artists_with_genres += 1
                            print(f"Found genres for {artist['name']}: {', '.join(genres)}")
                        else:
                            artists_without_genres += 1
                            print(f"No genres found for {artist['name']}")
                
                # Print batch summary
                print(f"\nBatch {current_batch} summary:")
                print(f"- Artists with genres: {artists_with_genres}")
                print(f"- Artists without genres: {artists_without_genres}")
                
            except requests.exceptions.RequestException as e:
                print(f"\nError fetching genres for batch: {str(e)}")
                if hasattr(e.response, 'text'):
                    print(f"Response: {e.response.text}")
                # Continue with next batch even if this one fails
                continue
        
        # Print final summary
        print(f"\n{'='*50}")
        print("Genre fetching complete!")
        print(f"Total artists processed: {len(unique_ids)}")
        print(f"Artists with genres: {artists_with_genres}")
        print(f"Artists without genres: {artists_without_genres}")
        print(f"{'='*50}")
        
        return genres_by_artist 