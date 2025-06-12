# Spotify Organizer Project Structure

```
spotify_organizer/
├── src/
│   ├── __init__.py
│   ├── spotify/
│   │   ├── __init__.py
│   │   ├── client.py          # Spotify connection and basic operations
│   │   └── liked_songs.py     # Functions for getting liked songs
│   ├── reccobeats/
│   │   ├── __init__.py
│   │   ├── client.py          # ReccoBeats connection and basic operations
│   │   ├── track_info.py      # Functions for getting track info/IDs
│   │   └── audio_features.py  # Functions for getting audio features
│   └── utils/
│       ├── __init__.py
│       ├── file_handler.py    # Functions for saving/loading JSON files
│       └── time_utils.py      # Time formatting and tracking utilities
├── scripts/
│   ├── get_liked_songs.py     # Script to get liked songs
│   ├── get_reccobeats_ids.py  # Script to get ReccoBeats IDs
│   └── get_audio_features.py  # Script to get audio features
├── data/
│   ├── raw/                   # Raw data files
│   └── processed/             # Processed data files
├── tests/
│   ├── __init__.py
│   ├── test_spotify.py
│   ├── test_reccobeats.py
│   └── test_utils.py
├── requirements.txt
└── README.md
```

## Directory Structure Explanation

### Source Code (src/)
- **Spotify Module**
  - `client.py`: Handles Spotify API authentication and basic operations
  - `liked_songs.py`: Functions for fetching and processing liked songs

- **RaccoonBeats Module**
  - `client.py`: Handles RaccoonBeats API connection
  - `track_info.py`: Functions for getting track information and IDs
  - `audio_features.py`: Functions for getting audio features

- **Utils Module**
  - `file_handler.py`: Functions for saving and loading JSON files
  - `time_utils.py`: Utilities for time formatting and tracking

### Scripts Directory
- Contains executable scripts for each major operation
- `get_liked_songs.py`: Fetches and saves liked songs from Spotify
- `get_reccobeats_ids.py`: Gets RaccoonBeats IDs for songs
- `get_audio_features.py`: Fetches audio features for songs

### Data Directory
- `raw/`: Stores raw data from APIs (e.g., liked songs JSON)
- `processed/`: Stores processed data (e.g., audio features)

### Tests Directory
- Contains test files for each module
- Simple test structure matching the source code

## Key Features
1. **Simple and Direct**: Each file has a clear, single responsibility
2. **Script-Based**: Easy to run individual operations
3. **Data Organization**: Clear separation between raw and processed data
4. **Modular**: Easy to maintain and extend
5. **Testable**: Simple test structure for each component 