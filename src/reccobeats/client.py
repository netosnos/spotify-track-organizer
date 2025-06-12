"""
RaccoonBeats API client implementation.
Handles basic API connection and requests.
"""
import requests
from typing import Dict, Any, Optional

class RaccoonBeatsClient:
    """Client for interacting with the RaccoonBeats API."""
    
    BASE_URL = "https://api.raccobeats.com/v1"  # Replace with actual base URL
    
    def __init__(self):
        """Initialize the RaccoonBeats client."""
        self.session = requests.Session()
    
    def _make_request(self, endpoint: str, method: str = "GET", params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make a request to the RaccoonBeats API.
        
        Args:
            endpoint (str): API endpoint to call
            method (str): HTTP method (default: GET)
            params (Dict, optional): Query parameters
            
        Returns:
            Dict[str, Any]: API response data
            
        Raises:
            Exception: If the API request fails
        """
        url = f"{self.BASE_URL}/{endpoint}"
        
        try:
            response = self.session.request(method, url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"RaccoonBeats API request failed: {str(e)}")
    
    def search_track(self, query: str) -> Dict[str, Any]:
        """
        Search for a track in RaccoonBeats.
        
        Args:
            query (str): Search query (usually track name and artist)
            
        Returns:
            Dict[str, Any]: Search results
        """
        return self._make_request("search", params={"q": query})
    
    def get_track_info(self, track_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a track.
        
        Args:
            track_id (str): RaccoonBeats track ID
            
        Returns:
            Dict[str, Any]: Track information
        """
        return self._make_request(f"tracks/{track_id}")
    
    def get_audio_features(self, track_id: str) -> Dict[str, Any]:
        """
        Get audio features for a track.
        
        Args:
            track_id (str): RaccoonBeats track ID
            
        Returns:
            Dict[str, Any]: Audio features data
        """
        return self._make_request(f"tracks/{track_id}/features") 