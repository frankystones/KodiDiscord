# 🎬 KodiDiscord 🎮
Discord Rich Presence for Kodi

## 📝 Prerequisites
* Kodi Nexus 20.0 or higher (19 and lower might not work with thumbnails)
* Python (version 3.x)
* A TMDB account

## 🚀 Installation
1. Clone the repository
2. Install the dependencies from `requirements.txt`
3. Rename `.env.example` to `.env`
4. Edit `.env` and fill in your TMDB API key

## ⚙️ Configuration
1. Edit `config.py` and make the following changes:
   * Set `IMDB_BUTTON_ENABLED` to either `False` or `True` to enable or disable IMDb buttons (see examples below)
   * Set `TMDB_BUTTON_ENABLED` to either `False` or `True` to enable or disable TMDb buttons (see examples below)
   * Set `TIME_REMAINING_RPC_ENABLED` to either `False` or `True` to include the time left in the RPC
   * Set `DIRECTOR_ENABLED` to either `False` or `True` to include the Directors in the RPC (movies only)
   * Set `GENRES_ENABLED` to either `False` or `True` to include the Genres (movies only)
   * **Note: `DIRECTOR_ENABLED` and `GENRES_ENABLED` can't be both True, one has to be False because Discord only allows 2 lines**

## 🎯 Usage
Run `main.py`

## 🎞️ Supported Media Types
* TV Shows 📺
* Movies 🎥
* Live TV (PVR IPTV Simple Client) 📡

## 📸 Examples
![image](https://github.com/zeroquinc/KodiDiscord/assets/39315068/848cbe27-d508-46c5-93dd-a8b9c72c92a1)

![image](https://github.com/zeroquinc/KodiDiscord/assets/39315068/e494b101-c764-4901-bd7d-a53aa186b0e4)

![image](https://github.com/zeroquinc/KodiDiscord/assets/39315068/e22e37c0-27a6-429a-a2c4-21e412aad10a)

## 💡 Future Ideas
* Add Music
* Try to make it a Kodi addon

## 📞 Contact
If you have any questions, please create an issue or add me on Discord 💬
