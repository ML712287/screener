import os
import json
import re
import time
import requests
from pathlib import Path

API = os.environ.get("YT_API_KEY", "")

# 預設財經台（唔指定就唔使改，想加台就加 handle）
CHANNELS = {
    "us":   ["@markets", "@BloombergTechnology", "@CNBCtelevision", "@YahooFinance"],
    "cn":   ["@CGTNBusiness", "@YicaiGlobal"],
    "asia": ["@CNBCInternational", "@BloombergTV"],
}
PER = 6           # 每區最多取幾條
MAXSEC = 7200     # 超過2小時當長節目/直播，跳過
OUT = Path(__file__).resolve().parent / "news.json"


def get(url, **p):
    p["key"] = API
    r = requests.get(url, params=p, timeout=30)
    r.raise_for_status()
    return r.json()


def uploads_id(handle):
    j = get("https://www.googleapis.com/youtube/v3/channels",
            part="contentDetails", forHandle=handle)
    items = j.get("items") or []
    if not items:
        return None
    return items[0]["contentDetails"]["relatedPlaylists"]["uploads"]


def iso_seconds(d):
    if not d:
        return 0
    m = re.findall(r"(\d+)([HMS])", d)
    s = 0
    for v, u in m:
        v = int(v)
        s += v * 3600 if u == "H" else v * 60 if u == "M" else v
    return s


def latest(uploads, n):
    ids = []
    tok = None
    while len(ids) < n * 4:
        j = get("https://www.googleapis.com/youtube/v3/playlistItems",
                part="contentDetails", playlistId=uploads,
                maxResults=50, pageToken=tok)
        for it in j.get("items", []):
            vid = it.get("contentDetails", {}).get("videoId")
            if vid:
                ids.append(vid)
        tok = j.get("nextPageToken")
        if not tok:
            break

    out = []
    for i in range(0, len(ids), 50):
        batch = ids[i:i + 50]
        if not batch:
            continue
        j = get("https://www.googleapis.com/youtube/v3/videos",
                part="snippet,contentDetails,status,liveStreamingDetails",
                id=",".join(batch))
        for v in j.get("items", []):
            # 剔走直播
            if v.get("liveStreamingDetails"):
                continue
            if v.get("snippet", {}).get("liveBroadcastContent", "none") != "none":
                continue
            # 剔走禁嵌入
            if v.get("status", {}).get("embeddable") is False:
                continue
            # 剔走太長
            dur = iso_seconds(v.get("contentDetails", {}).get("duration", "PT0S"))
            if dur <= 0 or dur > MAXSEC:
                continue
            out.append({
                "id": v["id"],
                "title": v["snippet"].get("title", ""),
                "pub": v["snippet"].get("publishedAt", ""),
            })
            if len(out) >= n:
                return out
    return out


def main():
    res = {"us": [], "cn": [], "asia": []}
    for cat, handles in CHANNELS.items():
        for h in handles:
            try:
                up = uploads_id(h)
                if up:
                    res[cat] += latest(up, PER)
            except Exception as e:
                print(f"skip {h}: {e}")
            time.sleep(0.2)

    # 去重、截短
    for cat in res:
        seen, tmp = set(), []
        for x in res[cat]:
            if x["id"] in seen:
                continue
            seen.add(x["id"])
            tmp.append(x)
        res[cat] = tmp[:PER]

    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    print("news.json saved:", {k: len(v) for k, v in res.items()})


if __name__ == "__main__":
    main()
