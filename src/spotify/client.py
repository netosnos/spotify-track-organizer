"""
Spotify API client implementation.
Handles authentication and provides methods to interact with the Spotify Web API.
"""
import os
from typing import Optional, Dict, Any
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
        
        while True:
            results = self.get_liked_songs(limit=limit, offset=offset)
            if not results['items']:
                break
                
            all_songs.extend(results['items'])
            offset += limit
            
            # If we got less than the limit, we've reached the end
            if len(results['items']) < limit:
                break
        
        return all_songs 