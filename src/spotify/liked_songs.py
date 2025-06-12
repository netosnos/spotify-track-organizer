"""
Functions for handling Spotify liked songs operations.
"""
from typing import List, Dict, Any
from .client import SpotifyClient

def get_all_liked_songs() -> List[Dict[str, Any]]:
    """
    Get all user's liked songs from Spotify.
    
    Returns:
        List[Dict[str, Any]]: List of liked songs with their details
    """
    client = SpotifyClient()
    return client.get_all_liked_songs()

def get_liked_songs_batch(limit: int = 50, offset: int = 0) -> Dict[str, Any]:
    """
    Get a batch of liked songs from Spotify.
    
    Args:
        limit (int): Maximum number of songs to return (default: 50)
        offset (int): Offset for pagination (default: 0)
        
    Returns:
        Dict[str, Any]: Dictionary containing the batch of liked songs
    """
    client = SpotifyClient()
    return client.get_liked_songs(limit=limit, offset=offset)

def extract_song_details(song: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract relevant details from a Spotify song object.
    
    Args:
        song (Dict[str, Any]): Raw song data from Spotify
        
    Returns:
        Dict[str, Any]: Dictionary with relevant song details
    """
    track = song['track']
    return {
        'id': track['id'],
        'name': track['name'],
        'artists': [artist['name'] for artist in track['artists']],
        'album': track['album']['name'],
        'duration_ms': track['duration_ms'],
        'popularity': track['popularity'],
        'added_at': song['added_at']
    } 