import os
import requests
import yt_dlp
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, APIC
import base64

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
    headers = {
        "Authorization": f"Basic {auth_header}"
    }
    data = {
        "grant_type": "client_credentials"
    }
    response = requests.post(auth_url, headers=headers, data=data)
    response_data = response.json()
    if 'access_token' in response_data:
        return response_data["access_token"]
    else:
        raise Exception("Failed to get Spotify access token. Check credentials.")

def fetch_spotify_metadata(title, artist):
    access_token = get_spotify_access_token()
    search_url = "https://api.spotify.com/v1/search"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    params = {
        "q": f"{title} {artist}",
        "type": "track",
        "limit": 1
    }
    response = requests.get(search_url, headers=headers, params=params)
    data = response.json()

    if data['tracks']['items']:
        track_info = data['tracks']['items'][0]
        track_title = track_info['name']
        track_artist = track_info['artists'][0]['name']
        album_art_url = track_info['album']['images'][0]['url']

        # Download album art
        album_art_filename = f"{track_title}.jpg".replace('/', '_')
        album_art_path = os.path.join(COVER_ART_DIR, album_art_filename)
        album_art_response = requests.get(album_art_url)
        with open(album_art_path, 'wb') as f:
            f.write(album_art_response.content)

        return album_art_path, track_title, track_artist
    return None, title, artist

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
        song_filename = f"{title}.mp3"

        # Fetch metadata from Spotify
        cover_filename, track_title, track_artist = fetch_spotify_metadata(title, artist)
        if cover_filename:
            new_song_filename = f"{track_title}.mp3".replace('/', '_')
            new_song_path = os.path.join(MUSIC_DIR, new_song_filename)

            # Rename MP3 file to match Spotify metadata
            os.rename(os.path.join(MUSIC_DIR, song_filename), new_song_path)

            return new_song_path, cover_filename, track_title, track_artist
        else:
            # If Spotify data not found, use original title
            song_path = os.path.join(MUSIC_DIR, song_filename)
            return song_path, 'CoverArt/default_cover.jpg', title, artist

def update_js_file(song_path, cover_path, display_name, artist_name):
    # Adjust the paths so that "Assets/" is removed from the path used in index.js
    song_rel_path = os.path.relpath(song_path, ASSETS_DIR).replace('\\', '/')
    cover_rel_path = os.path.relpath(cover_path, ASSETS_DIR).replace('\\', '/')

    with open(JS_FILE_PATH, 'r+') as js_file:
        content = js_file.read().strip()

        # Ensure there is a comma if other entries are present
        if content.endswith("}") and not content.endswith(",\n}"):
            content = content + ","

        new_song_entry = f"""    {{
        path: '{song_rel_path}',
        displayName: '{display_name}',
        cover: '{cover_rel_path}',
        artist: '{artist_name}'
    }},"""

        # Insert the new song entry before the closing bracket
        updated_content = content.replace("];", f"{new_song_entry}\n];")

        js_file.seek(0)
        js_file.write(updated_content)
        js_file.truncate()

def main():
    url = input("Enter the YouTube URL: ")

    try:
        # Download song and fetch metadata from Spotify
        song_path, cover_path, title, artist = download_song_and_cover(url)

        # Update the JS file
        update_js_file(song_path, cover_path, title, artist)
        print(f"Added {title} by {artist} to index.js")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
