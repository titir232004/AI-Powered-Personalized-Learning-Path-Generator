# fetchers/youtube_fetcher.py
import sys
import os
import requests
from dotenv import load_dotenv
load_dotenv()
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

YOUTUBE_API_KEY = ""


def fetch_youtube(skill_name, max_results=2):

    search_url = "https://www.googleapis.com/youtube/v3/search"

    params = {
        "part": "snippet",
        "q": f"{skill_name} tutorial playlist",
        "type": "playlist",
        "maxResults": max_results,
        "key": YOUTUBE_API_KEY
    }

    response = requests.get(search_url, params=params)
    data = response.json()

    playlists = []

    if "items" in data:

        for item in data["items"]:

            playlist_title = item["snippet"]["title"]
            playlist_id = item["id"]["playlistId"]

            playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"

            resource = {
                "skill": skill_name,
                "title": playlist_title,
                "url": playlist_url,
                "platform": "YouTube",
                "resource_type": "playlist"
            }

            playlists.append(resource)

            print(f"✅ {skill_name} playlist found: {playlist_title}")
            print(f"🔗 {playlist_url}\n")

    else:
        print(f"❌ No YouTube playlists found for {skill_name}")
        print(data)


    return playlists
