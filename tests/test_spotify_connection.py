"""
Test file for Spotify connection and basic functionality.
"""
import pytest
from src.spotify.client import SpotifyClient

def test_spotify_client_initialization():
    """Test that the Spotify client initializes correctly."""
    client = SpotifyClient()
    assert client.client_id is not None
    assert client.client_secret is not None
    assert client.redirect_uri is not None
    assert client.sp is not None

def test_get_liked_songs():
    """Test fetching liked songs."""
    client = SpotifyClient()
    songs = client.get_liked_songs(limit=1)
    assert 'items' in songs
    assert isinstance(songs['items'], list)

if __name__ == '__main__':
    # Simple manual test
    client = SpotifyClient()
    print("Testing Spotify connection...")
    songs = client.get_liked_songs(limit=1)
    print(f"Successfully fetched {len(songs['items'])} songs")
    if songs['items']:
        print("First song:", songs['items'][0]['track']['name']) 