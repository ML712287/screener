import os
import json
import requests
from datetime import datetime, timedelta

API_KEY = os.environ.get("YT_API_KEY")
CHANNELS = {
    "us": "UCUnTwTwfKSAjTDT_4Rblmg",
    "cn": "UCgrNz-aDmcr2uuto8_DL2jg",
    "asia": "UCo7a6riBFJ3tkeHjvkXPn1g"
}

def get_uploads_playlist(channel_id):
    url = f"https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id={channel_id}&key={API_KEY}"
    data = requests.get(url).json()
    if data.get("items"):
        return data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    return None

def fetch_videos(playlist_id):
    if not playlist_id: return []
    url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&maxResults=10&playlistId={playlist_id}&key={API_KEY}"
    data = requests.get(url).json()
    videos = []
    for item in data.get("videos", []):
        vid = item["snippet"]["resourceId"]["videoId"]
        title = item["snippet"]["title"]
        thumb = item["snippet"]["thumbnails"]["default"]["url"]
        videos.append({"id": vid, "title": title, "thumb": thumb})
    return videos

result = {}
for region, ch_id in CHANNELS.items():
    print(f"Fetching {region}...")
    pid = get_uploads_playlist(ch_id)
    result[region] = {
        "channel": ch_id,
        "videos": fetch_videos(pid)
    }

with open("news.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print("Done! news.json written.")
