import os
import json
import requests
import re

API_KEY = os.environ.get("YT_API_KEY", "").strip()
if not API_KEY:
    raise RuntimeError("YT_API_KEY not set")

CHANNELS = {
    "us": {"name": "Bloomberg Television", "channel_id": "UCUMZ7gOHsb0wTTv7m6fzH5g"},
    "cn": {"name": "CGTN", "channel_id": "UC2Q6tVZlwsEamPs6oQXo6Yg"},
    "asia": {"name": "CNBC International", "channel_id": "UCvDDvC2tXfW8Kj_m3oqd5qg"}
}

def get_uploads_pid(channel_id):
    r = requests.get("https://www.googleapis.com/youtube/v3/channels", params={
        "key": API_KEY, "id": channel_id, "part": "contentDetails"
    }, timeout=15).json()
    return r["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

def fetch_videos(playlist_id, max_results=10):
    r = requests.get("https://www.googleapis.com/youtube/v3/playlistItems", params={
        "key": API_KEY, "playlistId": playlist_id, "part": "snippet", "maxResults": max_results
    }, timeout=15).json()
    
    vids = [it["snippet"]["resourceId"]["videoId"] for it in r.get("items", [])]
    if not vids:
        return []
    
    r2 = requests.get("https://www.googleapis.com/youtube/v3/videos", params={
        "key": API_KEY, "id": ",".join(vids), "part": "snippet,contentDetails,status,liveStreamingDetails"
    }, timeout=15).json()
    
    results = []
    for v in r2.get("items", []):
        if v.get("status", {}).get("embeddable") is False:
            continue
        if v["snippet"].get("liveBroadcastContent") in ("live", "upcoming"):
            continue
        dur = v["contentDetails"]["duration"]
        mins = 0
        m = re.search(r'PT(?:(\d+)H)?(?:(\d+)M)?', dur)
        if m:
            mins = int(m.group(2) or 0) + int(m.group(1) or 0) * 60
        if mins > 30 or mins < 1:
            continue
        results.append({"id": v["id"], "title": v["snippet"]["title"], "channel": v["snippet"]["channelTitle"]})
        if len(results) >= 3:
            break
    return results

news = {}
for region, info in CHANNELS.items():
    try:
        pid = get_uploads_pid(info["channel_id"])
        news[region] = {"channel": info["name"], "videos": fetch_videos(pid)}
    except Exception as e:
        print(f"{region} error: {e}")
        news[region] = {"channel": info["name"], "videos": []}

with open("news.json", "w", encoding="utf-8") as f:
    json.dump(news, f, ensure_ascii=False, indent=2)
print("Done! news.json written.")
