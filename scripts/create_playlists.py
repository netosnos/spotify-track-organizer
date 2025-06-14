#!/usr/bin/env python3
"""
Script to create Spotify playlists based on audio features and genres.
"""
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os


class PlaylistCreator:

  def __init__(self, dry_run: bool = True):
    """Initialize the PlaylistCreator with Spotify client and file paths"""
    # Load environment variables
    load_dotenv()

    # Initialize Spotify client
    self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
      client_id=os.getenv('SPOTIFY_CLIENT_ID'),
      client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
      redirect_uri=os.getenv('SPOTIFY_REDIRECT_URI'),
      scope='playlist-modify-public playlist-modify-private'))

    # Get current user
    self.user_id = self.sp.current_user()['id']

    # File paths
    self.data_dir = Path('data/processed')
    self.audio_features_file = self.data_dir / 'tracks_with_audio_features.json'
    self.no_features_file = self.data_dir / 'tracks_without_raccobeats_ids.json'

    # Track counts
    self.total_tracks = 0
    self.processed_tracks = 0

    # Dry run mode
    self.dry_run = False  # Set to False to create real playlists

    # Playlist configurations
    self.playlists = {
      'Chill Vibes':
      'Soft, mellow, and relaxing tracks. Ideal for winding down or background ambiance.',
      'Feel-Good':
      'Happy, upbeat, and energizing songs that lift your mood.',
      'Sad & Moody':
      'Emotional, introspective, or melancholic songs. For reflective moments or sad vibes.',
      'Party Mode':
      'High-energy, danceable tracks. Perfect for getting the party started.',
      'Training & High Energy':
      'Fast-paced, energetic tracks to keep you moving during runs or cardio sessions.',
      'Driving Mix':
      'Songs with a balanced, rhythmic feel—great for road trips or long drives.',
      'Other':
      'A catch-all playlist for songs that don\'t have audio features or genre information.'
    }

    # Genre-based classification
    self.GENRES_BY_PLAYLIST = {
      'Chill Vibes': [
        'soft pop', 'acoustic pop', 'singer-songwriter', 'latin alternative',
        'neo soul', 'latin r&b', 'folk', 'folk rock', 'indie folk',
        'quiet storm', 'timba', 'bolero', 'bossa nova', 'latin jazz', 'jazz',
        'huayno', 'trova', 'nueva trova', 'vocal jazz', 'adult standards',
        'musicals'
      ],
      'Sad & Moody': [
        'sad sierreño', 'sierreño', 'latin folk', 'trova', 'nueva trova',
        'norteño', 'ranchera', 'corridos bélicos', 'corridos tumbados',
        'corrido', 'grupera', 'ballad', 'huayno', 'bolero', 'flamenco',
        'flamenco pop', 'flamenco urbano'
      ],
      'Feel-Good': [
        'latin pop', 'colombian pop', 'pop', 'pop rock', 'pop urbano',
        'soft pop', 'cumbia', 'cumbia norteña', 'vallenato', 'bachata',
        'salsa', 'merengue', 'música mexicana', 'pagode baiano', 'forró',
        'funk', 'funk pop', 'motown', 'tropical house', 'r&b', 'soul'
      ],
      'Party Mode': [
        'reggaeton', 'urbano latino', 'trap latino', 'argentine trap', 'rkt',
        'dembow', 'edm', 'electro house', 'dancehall', 'electrocumbia',
        'electro corridos', 'techengue', 'turreo', 'latin dance',
        'latin hip hop', 'latin afrobeats', 'latin', 'reggaeton chileno',
        'reggaeton mexa'
      ],
      'Training & High Energy': [
        'trap', 'rap', 'hip hop', 'trap latino', 'argentine trap', 'rock',
        'hard rock', 'punk', 'pop punk', 'metal', 'nu metal', 'electro house',
        'electro corridos', 'progressive house', 'latin rock',
        'rock en español', 'mexican rock', 'alternative metal',
        'progressive trance'
      ],
      'Driving Mix': [
        'rock en español', 'latin rock', 'rock', 'classic rock', 'soft rock',
        'mexican rock', 'argentine rock', 'pop rock', 'country',
        'country rock', 'americana', 'outlaw country', 'roots rock', 'britpop',
        'new wave', 'aor', 'yacht rock', 'synthpop'
      ]
    }

  def is_chill_vibes(self, features: Dict) -> bool:
    """Check if track matches Chill Vibes criteria"""
    return (features['valence'] <= 0.5 and features['energy'] <= 0.5
            and features['acousticness'] >= 0.3 and features['tempo'] <= 110
            and features['danceability'] <= 0.7)

  def is_sad_moody(self, features: Dict) -> bool:
    """Check if track matches Sad & Moody criteria"""
    return (features['valence'] <= 0.4 and features['energy'] <= 0.6
            and features['acousticness'] >= 0.2 and features['tempo'] <= 120)

  def is_feel_good(self, features: Dict) -> bool:
    """Check if track matches Feel-Good criteria"""
    return (features['valence'] >= 0.6 and features['energy'] >= 0.5
            and features['danceability'] >= 0.5
            and 85 <= features['tempo'] <= 140
            and features['acousticness'] <= 0.5)

  def is_party_mode(self, features: Dict) -> bool:
    """Check if track matches Party Mode criteria"""
    return (features['energy'] >= 0.6 and features['danceability'] >= 0.7
            and features['valence'] >= 0.5 and features['tempo'] >= 100
            and features['acousticness'] <= 0.4)

  def is_training_high_energy(self, features: Dict) -> bool:
    """Check if track matches Training & High Energy criteria"""
    return (features['energy'] >= 0.75 and features['tempo'] >= 120
            and features['danceability'] >= 0.5
            and features['acousticness'] <= 0.3)

  def is_driving_mix(self, features: Dict) -> bool:
    """Check if track matches Driving Mix criteria"""
    return (90 <= features['tempo'] <= 150 and 0.5 <= features['energy'] <= 0.9
            and features['danceability'] >= 0.5
            and features['acousticness'] <= 0.5)

  def classify_track(self, features: Dict) -> str:
    """Classify a track based on its audio features using flexible rules and best-match logic."""
    # Define playlist rules as (name, list of (feature, op, value))
    rules = [('Chill Vibes', [('valence', '<=', 0.5), ('energy', '<=', 0.5),
                              ('acousticness', '>=', 0.3),
                              ('tempo', '<=', 110),
                              ('danceability', '<=', 0.7)]),
             ('Sad & Moody', [('valence', '<=', 0.4), ('energy', '<=', 0.6),
                              ('acousticness', '>=', 0.2),
                              ('tempo', '<=', 120)]),
             ('Feel-Good', [('valence', '>=', 0.6), ('energy', '>=', 0.5),
                            ('danceability', '>=', 0.5),
                            ('tempo', 'range', (85, 140)),
                            ('acousticness', '<=', 0.5)]),
             ('Party Mode', [('energy', '>=', 0.6),
                             ('danceability', '>=', 0.7),
                             ('valence', '>=', 0.5), ('tempo', '>=', 100),
                             ('acousticness', '<=', 0.4)]),
             ('Training & High Energy', [('energy', '>=', 0.75),
                                         ('tempo', '>=', 120),
                                         ('danceability', '>=', 0.5),
                                         ('acousticness', '<=', 0.3)]),
             ('Driving Mix', [('tempo', 'range', (90, 150)),
                              ('energy', 'range', (0.5, 0.9)),
                              ('danceability', '>=', 0.5),
                              ('acousticness', '<=', 0.5)])]

    # Helper to check a single condition
    def check_condition(val, op, ref):
      if op == '<=':
        return val <= ref
      elif op == '>=':
        return val >= ref
      elif op == 'range':
        return ref[0] <= val <= ref[1]
      return False

    # Helper to compute difference for a single condition
    def diff_condition(val, op, ref):
      if op == '<=':
        return max(0, val - ref)
      elif op == '>=':
        return max(0, ref - val)
      elif op == 'range':
        if val < ref[0]:
          return ref[0] - val
        elif val > ref[1]:
          return val - ref[1]
        else:
          return 0
      return float('inf')

    # 1. Try to fully match a playlist
    for name, conds in rules:
      if all(
          check_condition(features.get(f, 0), op, val)
          for f, op, val in conds):
        return name

    # 2. If none fully match, count matches and compute total difference
    best_playlists = []
    max_matches = -1
    for name, conds in rules:
      matches = sum(
        check_condition(features.get(f, 0), op, val) for f, op, val in conds)
      if matches > max_matches:
        max_matches = matches
        best_playlists = [name]
      elif matches == max_matches:
        best_playlists.append(name)

    # 3. If tie, pick the one with smallest total difference
    if len(best_playlists) == 1:
      return best_playlists[0]
    else:
      min_diff = float('inf')
      best_name = best_playlists[0]
      for name, conds in rules:
        if name in best_playlists:
          total_diff = sum(
            diff_condition(features.get(f, 0), op, val)
            for f, op, val in conds)
          if total_diff < min_diff:
            min_diff = total_diff
            best_name = name
      return best_name

  def get_track_uri(self, track: Dict, use_id: bool = True) -> Optional[str]:
    """Get the Spotify URI for a track, using 'id' or 'spotify_id' as specified."""
    track_id = track.get('id') if use_id else track.get('spotify_id')
    if not track_id:
      print(f"\nWarning: Track missing ID: {track.get('name', 'Unknown')}")
      return None
    return f"spotify:track:{track_id}"

  def load_tracks(self) -> Tuple[List[Dict], List[Dict]]:
    """Load tracks from both JSON files"""
    print("\nLoading track data...")

    # Load tracks with audio features
    print("Reading tracks with audio features...")
    with open(self.audio_features_file, 'r') as f:
      audio_features_data = json.load(f)
      tracks_with_features = audio_features_data.get('tracks', [])
      print(f"Found {len(tracks_with_features)} tracks with audio features")

    # Load tracks without RaccoonBeats IDs (no audio features)
    print("Reading tracks without audio features...")
    with open(self.no_features_file, 'r') as f:
      no_features_data = json.load(f)
      tracks_without_features = no_features_data.get('tracks', [])
      print(
        f"Found {len(tracks_without_features)} tracks without audio features")

    self.total_tracks = len(tracks_with_features) + \
        len(tracks_without_features)
    return tracks_with_features, tracks_without_features

  def update_progress(self, message: str = None):
    """Update and display progress"""
    self.processed_tracks += 1
    percentage = (self.processed_tracks / self.total_tracks) * 100

    if message:
      print(f"\r{message} - {percentage:.1f}% complete", end='')
    else:
      print(f"\rProgress: {percentage:.1f}% complete", end='')

    if self.processed_tracks == self.total_tracks:
      print("\nDone!")

  def create_playlist(self, name: str, description: str) -> str:
    """Create a new playlist and return its ID"""
    if self.dry_run:
      print(f"\n[DRY RUN] Would create playlist: {name}")
      print(f"[DRY RUN] Description: {description}")
      return f"dry_run_{name}"

    try:
      playlist = self.sp.user_playlist_create(user=self.user_id,
                                              name=name,
                                              description=description,
                                              public=False)
      return playlist['id']
    except Exception as e:
      print(f"\nError creating playlist '{name}': {str(e)}")
      return None

  def add_tracks_to_playlist(self, playlist_id: str, track_uris: List[str]):
    """Add tracks to a playlist"""
    if not track_uris:
      return

    if self.dry_run:
      print(
        f"\n[DRY RUN] Would add {len(track_uris)} tracks to playlist {playlist_id}"
      )
      return

    try:
      # Spotify API allows adding 100 tracks at a time
      for i in range(0, len(track_uris), 100):
        batch = track_uris[i:i + 100]
        self.sp.playlist_add_items(playlist_id, batch)
        time.sleep(0.5)  # Small delay to avoid rate limiting
    except Exception as e:
      print(f"\nError adding tracks to playlist: {str(e)}")

  def classify_track_by_genre(self, track: Dict) -> str:
    """Classify a track without audio features by genre, using priority order."""
    # Gather all genres from all artists
    genres = set()
    for artist in track.get('artists', []):
      genres.update([g.lower() for g in artist.get('genres', [])])
    # Priority order
    for playlist in [
        'Chill Vibes', 'Sad & Moody', 'Feel-Good', 'Party Mode',
        'Training & High Energy', 'Driving Mix'
    ]:
      playlist_genres = set(self.GENRES_BY_PLAYLIST[playlist])
      if genres & playlist_genres:
        return playlist
    return 'Other'

  def run(self):
    """Main execution method"""
    try:
      print("Starting playlist creation process...")
      if self.dry_run:
        print("[DRY RUN MODE] No playlists will be created or modified")
      start_time = time.time()

      # Load tracks
      tracks_with_features, tracks_without_features = self.load_tracks()

      # Create playlists and store their IDs
      playlist_ids = {}
      for name, description in self.playlists.items():
        print(f"\nCreating playlist: {name}")
        playlist_id = self.create_playlist(name, description)
        if playlist_id:
          playlist_ids[name] = playlist_id

      # Process tracks with audio features
      print("\nProcessing tracks with audio features...")
      tracks_by_playlist = {name: [] for name in self.playlists.keys()}

      for track in tracks_with_features:
        features = track.get('audio_features', {})
        if features:
          playlist_name = self.classify_track(features)
          if playlist_name:
            track_uri = self.get_track_uri(track, use_id=True)
            if track_uri:
              tracks_by_playlist[playlist_name].append(track_uri)
        self.update_progress("Processing tracks with audio features")

      # Process tracks without audio features
      print("\nProcessing tracks without audio features...")
      for track in tracks_without_features:
        playlist_name = self.classify_track_by_genre(track)
        track_uri = self.get_track_uri(track, use_id=False)
        if track_uri:
          tracks_by_playlist[playlist_name].append(track_uri)
        self.update_progress("Processing tracks without audio features")

      # Add tracks to their respective playlists (dry run)
      print("\nAdding tracks to playlists...")
      for playlist_name, track_uris in tracks_by_playlist.items():
        if track_uris and playlist_name in playlist_ids:
          print(f"\nAdding {len(track_uris)} tracks to {playlist_name}")
          self.add_tracks_to_playlist(playlist_ids[playlist_name], track_uris)

      # Calculate and display total execution time
      total_time = time.time() - start_time
      print(f"\nTotal execution time: {total_time:.1f} seconds")

      # Print summary of tracks skipped due to missing IDs
      skipped_tracks = [
        track.get('name', 'Unknown') for track in tracks_without_features
        if not track.get('spotify_id')
      ]
      if skipped_tracks:
        print("\nTracks skipped due to missing IDs:")
        for name in skipped_tracks:
          print(f"- {name}")
        print(f"Total skipped: {len(skipped_tracks)}")

      # Print names of tracks without audio features that went to 'Other'
      other_uris = set(tracks_by_playlist.get('Other', []))
      other_tracks = [
        track for track in tracks_without_features
        if self.get_track_uri(track, use_id=False) in other_uris
      ]
      if other_tracks:
        print("\nTracks without audio features and assigned to 'Other':")
        for track in other_tracks:
          print(f"- {track.get('name', 'Unknown')}")
        print(f"Total in 'Other' (no audio features): {len(other_tracks)}")

    except Exception as e:
      print(f"\nError: {str(e)}")


def main():
  creator = PlaylistCreator(dry_run=True)  # Set to True for testing
  creator.run()


if __name__ == "__main__":
  main()
