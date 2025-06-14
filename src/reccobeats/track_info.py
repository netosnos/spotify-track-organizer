"""
Functions for getting track information and IDs from RaccoonBeats.
"""
from typing import Dict, Any, Optional, List
from .client import RaccoonBeatsClient


def search_track_by_name_and_artist(track_name: str, artist_name: str) -> Optional[Dict[str, Any]]:
  """
  Search for a track by name and artist.

  Args:
      track_name (str): Name of the track
      artist_name (str): Name of the artist

  Returns:
      Optional[Dict[str, Any]]: Track information if found, None otherwise
  """
  client = RaccoonBeatsClient()
  query = f"{track_name} {artist_name}"
  results = client.search_track(query)

  # TODO: Implement proper track matching logic
  # For now, return the first result if any
  return results.get('tracks', [{}])[0] if results.get('tracks') else None


def get_track_id(track_name: str, artist_name: str) -> Optional[str]:
  """
  Get RaccoonBeats track ID for a track.

  Args:
      track_name (str): Name of the track
      artist_name (str): Name of the artist

  Returns:
      Optional[str]: Track ID if found, None otherwise
  """
  track_info = search_track_by_name_and_artist(track_name, artist_name)
  return track_info.get('id') if track_info else None


def get_track_details(track_id: str) -> Dict[str, Any]:
  """
  Get detailed information about a track.

  Args:
      track_id (str): RaccoonBeats track ID

  Returns:
      Dict[str, Any]: Track details
  """
  client = RaccoonBeatsClient()
  return client.get_track_info(track_id)


def batch_get_track_ids(songs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
  """
  Get RaccoonBeats track IDs for a list of songs.

  Args:
      songs (List[Dict[str, Any]]): List of songs with name and artist information

  Returns:
      List[Dict[str, Any]]: List of songs with added RaccoonBeats track IDs
  """
  results = []
  for song in songs:
    track_id = get_track_id(song['name'], song['artists'][0])
    song_with_id = song.copy()
    song_with_id['raccobeats_id'] = track_id
    results.append(song_with_id)
  return results
