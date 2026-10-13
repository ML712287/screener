import time
from datetime import datetime

# ===== 模擬數據 (實際應用可對接 RSS 或 API) =====
macro = {
    "us 美國 CPI": "2.5%",
    "us ISM PMI": "54.9",
    "us 10年債": "5.19%",
    "cn 中國 PMI": "50.6"
}

stocks = [
    {"code": "AAPL", "name": "Apple"},
    {"code": "TSLA", "name": "Tesla"},
    {"code": "NVDA", "name": "NVIDIA"}
]

news_data = {
    "科技": [{"title": "AI 概念股持續炒上", "id": "dQw4w9WgXcQ"}],
    "財經": [{"title": "美債息率回落 大市反彈", "id": "9bZkp7q19f0"}]
}

season = "秋季"
position = "60%"

# ===== HTML/CSS 模板 =====
css = """
<style>
body{background:#111;color:#fff;font-family:sans-serif;margin:0;padding:20px}
.container{max-width:800px;margin:0 auto}
h1{color:#4fc3f7}
.sub{color:#aaa;margin-bottom:20px}
.macro{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:20px}
.mitem{background:#222;padding:10px 15px;border-radius:8px;text-align:center}
.label{color:#aaa;font-size:12px}
.val{font-size:20px;font-weight:bold;color:#4fc3f7}
.season-bar{background:#222;padding:10px 15px;border-radius:8px;margin-bottom:20px;display:flex;justify-content:space-between}
.news-sec{padding:20px;background:#1a1a1a;border-radius:12px;margin-bottom:20px}
.nc{display:flex;gap:10px;margin-bottom:15px;flex-wrap:wrap}
.nb{padding:8px 16px;border:1px solid #e94560;background:0;color:#e94560;border-radius:20px;cursor:pointer}
.nb.active,.nb:hover{background:#e94560;color:#fff}
.npw{margin-bottom:16px;display:none}
.npw.active{display:block}
.nvw{position:relative;padding-bottom:56.25%;height:0;overflow:hidden;border-radius:12px;background:#000}
.nvw iframe{position:absolute;top:0;left:0;width:100%;height:100%;border:0}
.nl{display:flex;flex-direction:column;gap:8px;max-height:300px;overflow-y:auto}
.ni{padding:10px;background:rgba(255,255,255,.05);border-radius:8px;cursor:pointer}
.ni:hover,.ni.active{background:rgba(233,69,96,.2)}
.grid{display:flex;gap:15px;flex-wrap:wrap}
.card{background:#222;padding:15px;border-radius:10px;min-width:120px;text-align:center}
</style>
"""

# ===== 組裝 HTML =====
macro_html = "".join(f'<div class="mitem"><div class="label">{k}</div><div class="val">{v}</div></div>' for k, v in macro.items())
cards_html = "".join(f'<div class="card"><h3>{s["code"]}</h3><p>{s["name"]}</p></div>' for s in stocks)

# 生成 News 區域
news_buttons = "".join(f'<button class="nb" onclick="fN(\'{k}\', this)">{k}</button>' for k in news_data.keys())
news_panels = ""
for region, items in news_data.items():
    list_html = "".join(f'<div class="ni" data-r="{region}" onclick="playV(\'{v["id"]}\', this)">{v["title"]}</div>' for v in items)
    news_panels += f"""
    <div class="npw" id="nv-{region}">
        <div class="nvw" id="player-{region}"></div>
        <div class="nl">{list_html}</div>
    </div>"""

news_html = f"""
<div class="news-sec">
    <h2>📰 最新新聞與影片</h2>
    <div class="nc">{news_buttons}</div>
    {news_panels}
</div>
"""

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
<div class="sub">Offline Screener · 最後更新：{current_time}</div>
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
    document.querySelectorAll('.npw').forEach(function(n) { n.style.display = 'none'; });
    document.getElementById('nv-' + region).style.display = 'block';
}
// 默認顯示第一個分類
window.onload = function() {
    var firstBtn = document.querySelector('.nb');
    if(firstBtn) { firstBtn.click(); }
}
</script>
"""
html += js_code + "\n</body>\n</html>"

with open("report.html", "w", encoding="utf-8") as f:
    f.write(html)
print("report.html generated!")
