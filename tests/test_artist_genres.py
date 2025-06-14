#!/usr/bin/env python3
"""
Test script to fetch genres for the first liked song's artist.
"""
import os
import time
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv


def get_artists_with_retry(url, headers, max_retries=3, initial_delay=1):
  """
  Make API request with retry logic for rate limiting.

  Args:
      url (str): API endpoint URL
      headers (dict): Request headers
      max_retries (int): Maximum number of retry attempts
      initial_delay (int): Initial delay between retries in seconds

  Returns:
      dict: Artists data
  """
  delay = initial_delay
  for attempt in range(max_retries):
    try:
      print(f"\nAttempt {attempt + 1} of {max_retries}")
      print(f"Waiting {delay} seconds before making request...")
      time.sleep(delay)  # Always wait before making a request

      print("Making API request...")
      response = requests.get(url, headers=headers)
      response.raise_for_status()
      return response.json()

    except requests.exceptions.HTTPError as e:
      if e.response.status_code == 429:  # Too Many Requests
        if attempt < max_retries - 1:  # Don't sleep on the last attempt
          retry_after = int(e.response.headers.get('Retry-After', delay))
          print(f"\nRate limited! Spotify says wait {retry_after} seconds")
          print(f"That's about {retry_after/3600:.2f} hours")

          # If the retry time is too long, we might want to stop
          if retry_after > 3600:  # More than 1 hour
            print("\nThe retry time is very long. This might indicate:")
            print("1. Too many requests in a short time")
            print("2. A temporary issue with Spotify's API")
            print("3. Your app might be rate limited")
            print("\nConsider waiting a few hours before trying again.")
            return None

          delay = retry_after
          continue
      raise
  return None


def main():
  """Test fetching artist genres."""
  try:
    # Load environment variables
    print("Loading environment variables...")
    load_dotenv()

    # Initialize Spotify client
    print("Initializing Spotify client...")
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
      client_id=os.getenv('SPOTIPY_CLIENT_ID'),
      client_secret=os.getenv('SPOTIPY_CLIENT_SECRET'),
      redirect_uri=os.getenv('SPOTIPY_REDIRECT_URI'),
      scope='user-library-read'))

    # Get the first few liked songs
    print("Fetching liked songs...")
    try:
      results = sp.current_user_saved_tracks(
        limit=5)  # Get 5 songs for testing
      print("Successfully fetched liked songs")
    except Exception as e:
      print(f"Error fetching liked songs: {str(e)}")
      return

    if not results['items']:
      print("No liked songs found!")
      return

    # Collect unique artist IDs
    artist_ids = set()
    for item in results['items']:
      song = item['track']
      print(f"\nSong: {song['name']}")
      for artist in song['artists']:
        print(f"Artist: {artist['name']}")
        artist_ids.add(artist['id'])

    # Convert set to list and take first 50 artists (Spotify's limit)
    artist_ids = list(artist_ids)[:50]
    print(f"\nFound {len(artist_ids)} unique artists")

    # Get artist details including genres using batch API call
    print("\nFetching artist details...")
    try:
      # Get the access token
      token = sp.auth_manager.get_cached_token()['access_token']

      # Make batch API call with retry logic
      print(f"Making batch API call for {len(artist_ids)} artists...")
      headers = {'Authorization': f'Bearer {token}'}

      # Join artist IDs with commas for the batch request
      ids_param = ','.join(artist_ids)
      artists = get_artists_with_retry(
        f'https://api.spotify.com/v1/artists?ids={ids_param}', headers)

      if artists and 'artists' in artists:
        print("Successfully received artist details")

        # Print genres for each artist
        print("\nGenres by artist:")
        for artist in artists['artists']:
          print(f"\n{artist['name']}:")
          if artist['genres']:
            for genre in artist['genres']:
              print(f"- {genre}")
          else:
            print("No genres found for this artist")
      else:
        print("Failed to get artist details after all retries")

    except requests.exceptions.RequestException as e:
      print(f"Error making API request: {str(e)}")
      if hasattr(e.response, 'text'):
        print(f"Response text: {e.response.text}")
      return

  except Exception as e:
    print(f"\nAn error occurred: {str(e)}")
    print("Full error details:", e.__class__.__name__)


if __name__ == "__main__":
  main()
