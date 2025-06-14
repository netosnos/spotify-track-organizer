"""
Simple test file for RaccoonBeats API.
"""
import requests


def test_reccobeats_api():
  """Test RaccoonBeats API with hardcoded Spotify IDs"""

  base_url = "https://api.reccobeats.com"

  # Hardcoded Spotify IDs for testing
  spotify_ids = [
    "0L4YCNRfXAoTvdpWeH2RGj",  # Begin Again
    "6GNRkaWUB0Lwc19SdkTgx8"  # Another track
  ]

  try:
    # Get track information
    track_url = f"{base_url}/v1/track"
    params = {'ids': ','.join(spotify_ids)}
    print(f"\nGetting track information from: {track_url}")
    response = requests.get(track_url, params=params)
    response.raise_for_status()

    # Parse the response
    content = response.json()
    tracks = content.get('content', [])

    # Print results
    print("\nTrack Information:")
    for track in tracks:
      print(f"\nTitle: {track.get('trackTitle', 'N/A')}")
      print(f"ReccoBeats ID: {track.get('id', 'N/A')}")
      print(
        f"Spotify ID: {track.get('href', 'N/A').split('/')[-1] if track.get('href') else 'N/A'}"
      )
      print(
        f"Artists: {', '.join(artist['name'] for artist in track.get('artists', []))}"
      )
      print(f"Duration: {track.get('durationMs', 'N/A')} ms")
      print(f"Popularity: {track.get('popularity', 'N/A')}")
      print(f"Spotify URL: {track.get('href', 'N/A')}")

  except requests.exceptions.RequestException as e:
    print(f"Error: {str(e)}")
    if hasattr(e.response, 'text'):
      print(f"Response: {e.response.text}")


if __name__ == "__main__":
  test_reccobeats_api()
