import os
import sys
import requests
import yt_dlp
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, APIC
import base64
import re

# Spotify API credentials
SPOTIFY_CLIENT_ID = "d723d8244f58499bb1f277b6307ee212"
SPOTIFY_CLIENT_SECRET = "2813a3c678e245ae93636c67c291eb10"

# Directory paths
ASSETS_DIR = os.path.join(os.path.expanduser("~"), "Desktop", "MP3 Player", "Assets")
MUSIC_DIR = os.path.join(ASSETS_DIR, "Music")
COVER_ART_DIR = os.path.join(ASSETS_DIR, "CoverArt")
JS_FILE_PATH = os.path.join(ASSETS_DIR, "index.js")

def get_spotify_access_token():
    auth_url = "https://accounts.spotify.com/api/token"
    auth_header = base64.b64encode(f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()).decode()
    headers = {"Authorization": f"Basic {auth_header}"}
    data = {"grant_type": "client_credentials"}
    response = requests.post(auth_url, headers=headers, data=data)
    response_data = response.json()
    if 'access_token' in response_data:
        return response_data["access_token"]
    else:
        raise Exception("Failed to get Spotify access token. Check credentials.")

def clean_title(title):
    # Patterns to remove extraneous phrases from the title
    patterns = [
        r"\bofficial music video\b",
        r"\bofficial audio\b",
        r"\blyrics?\b",
        r"\bvideo\b",
        r"\bfeat\b.*",         # Removes "feat." or "ft." and following text
        r"\bhd\b",              # Removes "HD"
        r"\bmv\b",              # Removes "MV"
        r"\([^)]+\)",           # Removes text within parentheses
        r"\[[^\]]+\]",          # Removes text within brackets
    ]
    for pattern in patterns:
        title = re.sub(pattern, '', title, flags=re.IGNORECASE)
    return title.strip()

def fetch_spotify_metadata(title, artist):
    # Clean up the title
    cleaned_title = clean_title(title)
    access_token = get_spotify_access_token()
    search_url = "https://api.spotify.com/v1/search"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"q": f"{cleaned_title} {artist}", "type": "track", "limit": 3}
    response = requests.get(search_url, headers=headers, params=params)
    data = response.json()

    if 'tracks' in data and data['tracks']['items']:
        for track_info in data['tracks']['items']:
            track_artist = track_info['artists'][0]['name'].lower()
            track_title = track_info['name'].lower()
            # Verify artist and title similarity
            if artist.lower() in track_artist or artist.lower() in track_title:
                album_art_url = track_info['album']['images'][0]['url']
                album_art_filename = f"{track_title}.jpg".replace('/', '_')
                album_art_path = os.path.join(COVER_ART_DIR, album_art_filename)
                album_art_response = requests.get(album_art_url)
                with open(album_art_path, 'wb') as f:
                    f.write(album_art_response.content)
                return album_art_path, track_info['name'], track_info['artists'][0]['name']

    # If no accurate match found, use the cleaned title and default artist format
    default_cover_path = os.path.join(COVER_ART_DIR, 'default_cover.jpg')
    cleaned_artist = artist.title()
    fallback_title = clean_title(title)  # Additional cleanup for fallback title
    return default_cover_path, fallback_title, cleaned_artist

def download_song_and_cover(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(MUSIC_DIR, '%(title)s.%(ext)s'),
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }
        ]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        title = info.get('title')
        artist = info.get('uploader') or 'Unknown Artist'
        song_filename = os.path.join(MUSIC_DIR, f"{title}.mp3")

        # Fetch metadata from Spotify
        cover_filename, track_title, track_artist = fetch_spotify_metadata(title, artist)
        if cover_filename:
            new_song_filename = os.path.join(MUSIC_DIR, f"{track_title}.mp3").replace('/', '_')
            os.rename(song_filename, new_song_filename)

            return new_song_filename, cover_filename, track_title, track_artist
        else:
            # If Spotify data not found, use the cleaned fallback title
            cleaned_fallback_title = clean_title(title)
            fallback_filename = os.path.join(MUSIC_DIR, f"{cleaned_fallback_title}.mp3")
            os.rename(song_filename, fallback_filename)

            return fallback_filename, os.path.join(COVER_ART_DIR, 'default_cover.jpg'), cleaned_fallback_title, artist

def update_js_file(song_path, cover_path, display_name, artist_name):
    # Adjust paths so "Assets/" is removed from paths used in index.js
    song_rel_path = os.path.relpath(song_path, ASSETS_DIR).replace('\\', '/')
    cover_rel_path = os.path.relpath(cover_path, ASSETS_DIR).replace('\\', '/')

    with open(JS_FILE_PATH, 'r+') as js_file:
        content = js_file.read().strip()

        # Ensure comma if other entries are present
        if content.endswith("}") and not content.endswith(",\n}"):
            content = content + ","

        new_song_entry = f"""    {{
        path: '{song_rel_path}',
        displayName: '{display_name}',
        cover: '{cover_rel_path}',
        artist: '{artist_name}'
    }},"""

        # Insert new song entry before the closing bracket
        updated_content = content.replace("];", f"{new_song_entry}\n];")

        js_file.seek(0)
        js_file.write(updated_content)
        js_file.truncate()

def main(youtube_url):
    try:
        # Download song and fetch metadata from Spotify
        song_path, cover_path, title, artist = download_song_and_cover(youtube_url)

        # Update the JS file
        update_js_file(song_path, cover_path, title, artist)
        print(f"Added {title} by {artist} to index.js")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    youtube_url = sys.argv[1]  # Get the URL argument
    main(youtube_url)
