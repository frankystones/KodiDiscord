import time
import requests
from pypresence.exceptions import PipeClosed
from datetime import datetime, timedelta

from config import IMDB_BUTTON_ENABLED
from .tmdb import get_tmdb_id, get_media_type, get_image_url, get_imdb_id, get_imdb_url
from .globals import RPC, INFO_URL, LENGTH_URL
from .custom_logger import get_logger

logger = get_logger(__name__)

# Initialize global variables
result = None
previous_info = None
session = requests.Session()  # Create a Session object

# Create dictionaries for caching
tmdb_id_cache = {}
imdb_id_cache = {}
media_type_cache = {}
image_url_cache = {}
imdb_url_cache = {}

# Function to set the RP with the provided info and length
def set_rp(info, length):
    global previous_info, previous_speed
    info = info['result']['item']
    length = length['result']
    if previous_info == info and previous_speed == length['speed']:  # Check if both info and speed are the same as before to prevent unnecessary updates
        return
    start_time = calculate_start_time(length)
    end_time = calculate_end_time(start_time, length)

    # Create a unique string key from the info dictionary
    info_key = f"{info['type']}_{info['id']}"

    # Use the string key in the cache
    tmdb_id = tmdb_id_cache.get(info_key)
    if tmdb_id is None:
        tmdb_id = get_tmdb_id(info)
        tmdb_id_cache[info_key] = tmdb_id

    imdb_id = imdb_id_cache.get(info_key)
    if imdb_id is None:
        imdb_id = get_imdb_id(info)
        imdb_id_cache[info_key] = imdb_id

    media_type = media_type_cache.get(info_key)
    if media_type is None:
        media_type = get_media_type(info)
        media_type_cache[info_key] = media_type

    image_key = f"{tmdb_id}_{media_type}"
    image_url = image_url_cache.get(image_key)
    if image_url is None:
        image_url = get_image_url(tmdb_id, media_type)
        image_url_cache[image_key] = image_url

    imdb_url = imdb_url_cache.get(imdb_id)
    if imdb_url is None:
        imdb_url = get_imdb_url(imdb_id)
        imdb_url_cache[imdb_id] = imdb_url

    if info['type'] == 'movie':
        # If the media type is a movie, update the RP accordingly
        update_rpc_movie(info, length, start_time, end_time, image_url, imdb_url)
    elif info['type'] == 'episode':
        # If the media type is an episode, update the RP accordingly
        update_rpc_episode(info, length, start_time, end_time, image_url, imdb_url)
    elif info['type'] == 'channel':
        # If the media type is a channel, update the RP accordingly
        update_rpc_channel(info, length, start_time, end_time, image_url)
    elif info['type'] == 'unknown' and length['speed'] == 0:
        # If nothing is playing, log an info message and clear the RP
        logger.info("Nothing is playing. Clearing RPC...")
        RPC.clear()

    previous_info = info
    previous_speed = length['speed']
    
    # Log the current time and total time for debugging
    logger.debug(f"Current time: {length['time']}")
    logger.debug(f"Total time: {length['totaltime']}")

# Function to fetch information from a session
def fetch_info(session):
    for i in range(5):  # Retry up to 5 times
        try:
            # Return the JSON response from the session's INFO_URL
            response = session.get(INFO_URL).json()
            time.sleep(3)  # Sleep for 3 seconds
            return response
        except requests.exceptions.RequestException as e:
            # Log an error message if there's a connection issue and wait for an exponentially increasing amount of time before the next attempt
            logger.error(f"Can't connect to Kodi web interface: {e}. Are you sure it's running? Is the web interface on?")
            time.sleep(2 ** i)  # Exponential backoff

# Function to fetch the length of a session
def fetch_length(session):
    for i in range(5):  # Retry up to 5 times
        try:
            # Return the JSON response from the session's LENGTH_URL
            response = session.get(LENGTH_URL).json()
            time.sleep(3)  # Sleep for 3 seconds
            return response
        except requests.exceptions.RequestException as e:
            # Log an error message if there's a connection issue and wait for an exponentially increasing amount of time before the next attempt
            logger.error(f"Can't connect to Kodi web interface: {e}. Are you sure it's running? Is the web interface on?")
            time.sleep(2 ** i)  # Exponential backoff

# Function to update the Rich Presence (RP) with the provided info and length
def update_rp(info, length):
    try:
        # Set the RP with the provided info and length
        set_rp(info, length)
    except PipeClosed:
        # If the connection to Discord is lost, log an info message and attempt to reconnect
        logger.info("Connection to Discord lost. Attempting to reconnect...")
        RPC.connect()

# The following functions update the RP based on the type of media (movie, episode, channel) and whether it's playing or paused

# Function to update the RP for a movie
def update_rpc_movie(info, length, start_time, end_time, image_url, imdb_url):
    if length['speed'] == 0:
        # If the movie is paused, update the RP accordingly
        update_rpc_paused_movie(info, image_url, imdb_url)
    else:
        # If the movie is playing, update the RP accordingly
        update_rpc_playing_movie(info, start_time, end_time, image_url, imdb_url)

# Function to update the RP for an episode
def update_rpc_episode(info, length, start_time, end_time, image_url, imdb_url):
    if length['speed'] == 0:
        # If the episode is paused, update the RP accordingly
        update_rpc_paused_episode(info, image_url, imdb_url)
    else:
        # If the episode is playing, update the RP accordingly
        update_rpc_playing_episode(info, start_time, end_time, image_url, imdb_url)

# Function to update the RP for a channel
def update_rpc_channel(info, length, start_time, end_time, image_url):
    if length['speed'] == 0:
        # If the channel is paused, update the RP accordingly
        update_rpc_paused_channel(info, image_url)
    elif length['time']['hours'] == 0 and length['time']['minutes'] == 0 and length['time']['seconds'] == 0 and length['totaltime']['hours'] == 0 and length['totaltime']['minutes'] == 0 and length['totaltime']['seconds'] == 0:
        # If start_time and end_time are both zero, update the RP without them, for EPG without information about start and end time
        update_rpc_playing_channel_without_time(info, image_url)
    else:
        # If the channel is playing, update the RP accordingly
        update_rpc_playing_channel(info, start_time, end_time, image_url)

# The following functions update the RP based on the type of media (movie, episode, channel) and whether it's playing or paused

# Function to update the RP when a movie is paused
def update_rpc_paused_movie(info, image_url, imdb_url):
    logger.info(f"Updated RPC")
    logger.info(f"Paused movie - {info['title']}")
    
    buttons = []
    if IMDB_BUTTON_ENABLED and imdb_url:
        buttons.append({"label": "IMDb", "url": imdb_url})
    
    rpc_params = {
        "details": str(info['title']),
        "state": "Paused...",
        "large_image": image_url,
        "large_text": 'Watching a movie on Kodi',
        "small_image": 'pause',
        "small_text": 'Paused'
    }
    
    if buttons:
        rpc_params["buttons"] = buttons

    RPC.update(**rpc_params)

# Function to update the RP when a movie is playing
def update_rpc_playing_movie(info, start_time, end_time, image_url, imdb_url):
    logger.info(f"Updated RPC")
    logger.info(f"Playing movie - {info['title']}")
    
    buttons = []
    if IMDB_BUTTON_ENABLED and imdb_url:
        buttons.append({"label": "IMDb", "url": imdb_url})
    
    rpc_params = {
        "details": str(info['title']),
        "start": start_time,
        "end": end_time,
        "large_image": image_url,
        "large_text": 'Watching a movie on Kodi',
        "small_image": 'play',
        "small_text": 'Playing'
    }
    
    if buttons:
        rpc_params["buttons"] = buttons

    RPC.update(**rpc_params)

# Function to update the RP when an episode is paused
def update_rpc_paused_episode(info, image_url, imdb_url):
    state_info = get_state_info(info)
    logger.info(f"Updated RPC")
    logger.info(f"Paused episode - {info['showtitle']} {state_info}")
    
    buttons = []
    if IMDB_BUTTON_ENABLED and imdb_url:
        buttons.append({"label": "IMDb", "url": imdb_url})
    
    rpc_params = {
        "state": state_info,
        "details": str(info['showtitle']),
        "large_image": image_url,
        "large_text": 'Watching a TV Show on Kodi',
        "small_image": 'pause',
        "small_text": 'Paused'
    }
    
    if buttons:
        rpc_params["buttons"] = buttons

    RPC.update(**rpc_params)

# Function to update the RP when an episode is playing
def update_rpc_playing_episode(info, start_time, end_time, image_url, imdb_url):
    state_info = get_state_info(info)
    logger.info(f"Updated RPC")
    logger.info(f"Playing episode - {info['showtitle']} {state_info}")
    
    buttons = []
    if IMDB_BUTTON_ENABLED and imdb_url:
        buttons.append({"label": "IMDb", "url": imdb_url})
    
    rpc_params = {
        "state": state_info,
        "details": str(info['showtitle']),
        "start": start_time,
        "end": end_time,
        "large_image": image_url,
        "large_text": 'Watching a TV Show on Kodi',
        "small_image": 'play',
        "small_text": 'Playing'
    }
    
    if buttons:
        rpc_params["buttons"] = buttons

    RPC.update(**rpc_params)

# Function to update the RP when a channel is paused
def update_rpc_paused_channel(info, image_url):
    title = get_title(info)
    logger.info(f"Updated RPC")
    logger.info(f"Paused channel - {info['label']}")
    RPC.update(state=title,
               details=str(info['label']),
               large_image=image_url,
               large_text='Watching Live TV on Kodi',
               small_image='pause',
               small_text='Paused')

# Function to update the RP when a channel is playing
def update_rpc_playing_channel(info, start_time, end_time, image_url):
    title = get_title(info)
    logger.info(f"Updated RPC")
    logger.info(f"Playing channel - {info['label']}")
    RPC.update(state=title,
                details=str(info['label']),
                start=start_time,
                end=end_time,
                large_image=image_url,
                large_text='Watching Live TV on Kodi',
                small_image='play',
                small_text='Playing')
    
# Function to update the RP when a channel is playing without start and end time
def update_rpc_playing_channel_without_time(info, image_url):
    title = get_title(info)
    logger.info(f"Updated RPC")
    logger.info(f"Playing channel - {info['label']}")
    RPC.update(state=title,
               details=str(info['label']),
               large_image=image_url,
               large_text='Watching Live TV on Kodi',
               small_image='play',
               small_text='Playing')

# Function to calculate the start time of a media
def calculate_start_time(length):
    return (datetime.now() - timedelta(hours=length["time"]['hours'], minutes=length["time"]['minutes'], seconds=length["time"]['seconds'])).timestamp()

# Function to calculate the end time of a media
def calculate_end_time(start_time, length):
    start_time = datetime.fromtimestamp(start_time)
    return (start_time + timedelta(hours=length['totaltime']['hours'], minutes=length['totaltime']['minutes'], seconds=length['totaltime']['seconds'])).timestamp()

# Function to get the state info of a media
def get_state_info(info):
    season_number = str(info['season']).zfill(2)
    episode_number = str(info['episode']).zfill(2)
    return f'S{season_number}E{episode_number}: {info["title"]}'

# Function to get the title of a media
def get_title(info):
    try:
        title = str(info['title'])
        if not title:
            title = 'Unknown'
    except KeyError:
        title = 'Unknown'
    return title