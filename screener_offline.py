import time

# ===== 模擬數據 =====
news_data = {
    "HK": {
        "videos": [
            {"id": "dQw4w9WgXcQ", "title": "Test Video 1"},
            {"id": "9bZkp7q19f0", "title": "Test Video 2"}
        ]
    },
    "US": {
        "videos": [
            {"id": "L_jWHffIx5E", "title": "Test Video 3"}
        ]
    }
}

macro = {"恒指": "18000", "納指": "15000"}
stocks = [{"code": "00700", "name": "騰訊"}]
season = "Q4"
position = "50%"

# ===== 生成 News Section HTML =====
def generate_news_html(news_data):
    if not news_data: return ""
    regions = list(news_data.keys())
    first_region = regions[0] if regions else ""
    
    html = f'<div class="news-sec"><h2>News</h2>'
    html += f'<div class="nc">'
    for r in regions:
        active = " active" if r == first_region else ""
        html += f'<button class="nb{active}" onclick="fN(\'{r}\',this)">{r.upper()}</button>'
    html += '</div>'
    
    for r in regions:
        display = "" if r == first_region else "none"
        html += f'<div id="nv-{r}" style="display:{display}">'
        html += f'<div class="npw"><div class="nvw" id="player-{r}"></div></div>'
        html += f'<div class="nl">'
        for v in news_data[r].get("videos", []):
            html += f'<div class="ni" data-r="{r}" onclick="playV(\'{v["id"]}\',this)"><span class="nf">{v["title"]}</span></div>'
        html += '</div></div>'
    html += '</div>'
    return html

# ===== CSS =====
css = """
<style>
.news-sec{padding:20px;background:#111;color:#fff;margin-top:20px;border-radius:12px}
.nc{display:flex;gap:10px;margin-bottom:15px;flex-wrap:wrap}
.nb{padding:8px 16px;border:1px solid #e94560;background:0;color:#e94560;border-radius:20px;cursor:pointer}
.nb.active,.nb:hover{background:#e94560;color:#fff}
.npw{margin-bottom:16px}
.nvw{position:relative;padding-bottom:56.25%;height:0;overflow:hidden;border-radius:12px}
.nvw iframe{position:absolute;top:0;left:0;width:100%;height:100%}
.nl{display:flex;flex-direction:column;gap:8px;max-height:300px;overflow-y:auto}
.ni{padding:10px;background:rgba(255,255,255,.05);border-radius:8px;cursor:pointer}
.ni:hover,.ni.active{background:rgba(233,69,96,.2)}
</style>
"""

# ===== 組裝 HTML =====
macro_html = "".join(f'<div class="mitem"><div class="label">{k}</div><div class="val">{v}</div></div>' for k, v in macro.items())
cards_html = "".join(f'<div class="card"><h3>{s["code"]}</h3><p>{s["name"]}</p></div>' for s in stocks)
news_html = generate_news_html(news_data)

# 使用 time.strftime 替代 datetime，徹底解決報錯
current_time = time.strftime('%Y-%m-%d %H:%M')

html = f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<title>股票篩選器</title>
{css}
</head>
<body>
<div class="container">
<h1>📊 智能股票篩選器</h1>
<div class="sub">最後更新：{current_time}</div>
<div class="macro">{macro_html}</div>
<div class="season-bar"><span>🗓️ 季節：<strong>{season}</strong></span><span class="pos">建議倉位：{position}</span></div>
{news_html}
<div class="grid">{cards_html}</div>
</div>
"""

# ===== JS =====
js_code = """
<script>
var tag = document.createElement('script');
tag.src = "https://www.youtube.com/iframe_api";
var firstScriptTag = document.getElementsByTagName('script')[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

var players = {};
function onYouTubeIframeAPIReady() {
    document.querySelectorAll('.nvw').forEach(function(el) {
        var region = el.id.replace('player-','');
        players[region] = new YT.Player(el.id, { height: '100%', width: '100%', playerVars: { 'playsinline': 1 } });
    });
}
function playV(id, el) {
    var region = el.getAttribute('data-r');
    if(players[region]) {
        players[region].loadVideoById(id);
        players[region].playVideo();
    }
    document.querySelectorAll('.ni.active').forEach(function(n) { n.classList.remove('active'); });
    el.classList.add('active');
}
function fN(region, btn) {
    document.querySelectorAll('.nb.active').forEach(function(n) { n.classList.remove('active'); });
    btn.classList.add('active');
    document.querySelectorAll('[id^="nv-"]').forEach(function(n) { n.style.display = 'none'; });
    document.getElementById('nv-' + region).style.display = '';
}
</script>
"""
html += js_code + "\n</body>\n</html>"

# ===== 寫入檔案 =====
with open("report.html", "w", encoding="utf-8") as f:
    f.write(html)
print("report.html generated!")
