import requests
import json
import urllib.parse
from .custom_logger import logger

from .globals import BASE_URL

def get_active_player():
    """Get active player ID"""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "Player.GetActivePlayers"
    }
    response = requests.post(BASE_URL, json=payload)
    data = response.json()

    if data.get("result"):
        return data["result"][0]["playerid"] 
    return None

def get_artwork(player_id):
    """Get the artwork of the currently playing item"""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "Player.GetItem",
        "params": {
            "playerid": player_id,
            "properties": ["art"]
        }
    }
    response = requests.post(BASE_URL, json=payload)
    data = response.json()

    return data.get("result", {}).get("item", {}).get("art", {})

def clean_url(kodi_url):
    """Removes the 'image://' prefix and decodes the URL"""
    if kodi_url.startswith("image://"):
        kodi_url = kodi_url[len("image://"):]  
    return urllib.parse.unquote(kodi_url)  

def get_thumbnail_url():
    player_id = get_active_player()
    if player_id is not None:
        artwork = get_artwork(player_id)
        thumb_url = artwork.get("thumb", "")

        if thumb_url:
            url = clean_url(thumb_url)
            logger.debug("URL thumb: {}", url)
            return url  
        else:
            logger.debug("No thumbs available")
            return None  
    else:
        logger.debug("No active players found")
        return None 