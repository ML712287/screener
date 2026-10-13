import json
import os
from datetime import datetime

# ===== 讀 news.json =====
news_data = {}
if os.path.exists("news.json"):
    try:
        with open("news.json", "r", encoding="utf-8") as f:
            news_data = json.load(f)
    except:
        pass

# ===== 模擬數據 =====
macro = {
    "US CPI": "2.5%", "US ISM PMI": "54.9", "US Fed Rate": "4.25%~4.50%",
    "China CPI": "0.3%", "Gold": "2,650", "Oil (WTI)": "71.2"
}
season = "秋季（偏防禦）"
position = "50% ~ 60%"
stocks = [
    {"code": "0002.HK", "name": "中電控股", "rating": "A", "price": 65.2, "entry": "62.0-63.5", "target": 70.0, "note": "高息公用，防守之選"},
    {"code": "0003.HK", "name": "香港中華煤氣", "rating": "A-", "price": 12.8, "entry": "12.0-12.5", "target": 14.5, "note": "穩定現金流"},
    {"code": "0700.HK", "name": "騰訊控股", "rating": "B+", "price": 420.0, "entry": "400-410", "target": 480.0, "note": "AI概念回調吸納"},
]

# ===== 新聞區 HTML =====
def news_section():
    if not news_data:
        return ""
    all_v = []
    for reg, info in news_data.items():
        for v in info.get("videos", []):
            all_v.append({"id": v["id"], "title": v["title"], "channel": v.get("channel", info["channel"]), "region": reg,
                          "rname": {"us": "🇺🇸 美國", "cn": "🇨🇳 中國", "asia": "🌏 亞洲"}.get(reg, reg)})
    if not all_v:
        return ""
    first = all_v[0]
    items = "".join(f'<div class="ni" data-r="{v["region"]}" onclick="playV(\'{v["id"]}\',this)"><span class="nf">{v["rname"]}</span><span class="nt">{v["title"][:55]}{"..." if len(v["title"])>55 else ""}</span></div>' for v in all_v)
    btns = '<button class="nb active" onclick="fN(\'all\',this)">全部</button><button class="nb" onclick="fN(\'us\',this)">🇺🇸 美國</button><button class="nb" onclick="fN(\'cn\',this)">🇨🇳 中國</button><button class="nb" onclick="fN(\'asia\',this)">🌏 亞洲</button>'
    return f"""
<style>
.news-sec{{margin:32px 0;padding:24px;background:linear-gradient(135deg,#1a1a2e,#16213e);border-radius:16px;box-shadow:0 8px 32px rgba(0,0,0,.3)}}
.news-sec h2{{color:#e94560;margin-bottom:16px}}
.nc{{display:flex;gap:8px;margin-bottom:16px;flex-wrap:wrap}}
.nb{{padding:8px 16px;border:1px solid #e94560;background:0;color:#e94560;border-radius:20px;cursor:pointer;transition:.3s;font-size:14px}}
.nb.active,.nb:hover{{background:#e94560;color:#fff}}
.npa{{display:grid;grid-template-columns:2fr 1fr;gap:16px}}
.nvw{{position:relative;padding-bottom:56.25%;height:0;overflow:hidden;border-radius:12px}}
.nvw iframe{{position:absolute;top:0;left:0;width:100%;height:100%}}
.nl{{max-height:315px;overflow-y:auto;display:flex;flex-direction:column;gap:8px}}
.ni{{display:flex;align-items:flex-start;gap:8px;padding:10px;background:rgba(255,255,255,.05);border-radius:8px;cursor:pointer;transition:.2s}}
.ni:hover,.ni.active{{background:rgba(233,69,96,.2)}}
.nf{{font-size:12px;white-space:nowrap}}
.nt{{font-size:13px;color:#ccc;line-height:1.4}}
@media(max-width:768px){{.npa{{grid-template-columns:1fr}}}}
</style>
<section class="news-sec">
<h2>📺 國際財經新聞</h2>
<div class="nc">{btns}</div>
<div class="npa">
<div class="nvw"><iframe id="nf" src="https://www.youtube-nocookie.com/embed/{first['id']}?rel=0" frameborder="0" allowfullscreen></iframe></div>
<div class="nl">{items}</div>
</div>
</section>
<script>
const AV={json.dumps(all_v, ensure_ascii=False)};
let CF='all',RT=null;
function playV(i,e){{document.getElementById('nf').src='https://www.youtube-nocookie.com/embed/'+i+'?autoplay=1&rel=0';document.querySelectorAll('.ni').forEach(x=>x.classList.remove('active'));if(e)e.classList.add('active');if(RT){{clearInterval(RT);RT=setInterval(AR,60000)}}}}
function fN(r,b){{CF=r;document.querySelectorAll('.nb').forEach(x=>x.classList.remove('active'));if(b)b.classList.add('active');document.querySelectorAll('.ni').forEach(x=>{{x.style.display=(r==='all'||x.dataset.r===r)?'flex':'none'}})}}
let RI=0;function AR(){{const V=AV.filter(x=>CF==='all'||x.region===CF);if(V.length<=1)return;RI=(RI+1)%V.length;playV(V[RI].id,null)}}
RT=setInterval(AR,60000);
</script>"""

# ===== 股票卡片 =====
def stock_card(s):
    colors = {"A": "#00ff88", "A-": "#88ff00", "B+": "#ffaa00", "B": "#ff8800", "C": "#ff4444"}
    c = colors.get(s["rating"], "#888")
    return f'''
<div class="card">
<div class="card-header"><span class="code">{s["code"]}</span><span class="rating" style="background:{c}20;color:{c};border:1px solid {c}">{s["rating"]}</span></div>
<div class="name">{s["name"]}</div>
<div class="price">${s["price"]}</div>
<div class="bar"><div class="fill" style="width:{min(s["price"]/s["target"]*100,100)}%;background:{c}"></div></div>
<div class="info"><span>入貨位: {s["entry"]}</span><span>目標: ${s["target"]}</span></div>
<div class="note">{s["note"]}</div>
</div>'''

# ===== 完整 HTML =====
css = """
<style>
body{font-family:'Segoe UI',sans-serif;background:linear-gradient(135deg,#0f0c29,#302b63,#24243e);color:#e0e0e0;margin:0;padding:20px;min-height:100vh}
.container{max-width:1200px;margin:0 auto}
h1{text-align:center;color:#fff;font-size:2em;margin-bottom:.2em}
.sub{text-align:center;color:#aaa;margin-bottom:24px}
.macro{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-bottom:24px}
.mitem{background:rgba(255,255,255,.08);padding:16px;border-radius:12px;text-align:center;backdrop-filter:blur(10px)}
.mitem .label{font-size:12px;color:#aaa}.mitem .val{font-size:20px;font-weight:bold;color:#e94560}
.season-bar{background:rgba(255,255,255,.08);padding:16px;border-radius:12px;margin-bottom:24px;display:flex;justify-content:space-between;align-items:center}
.season-bar .pos{font-size:24px;font-weight:bold;color:#00ff88}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:20px}
.card{background:linear-gradient(145deg,rgba(255,255,255,.1),rgba(255,255,255,.05));border:1px solid rgba(255,255,255,.15);border-radius:16px;padding:20px;backdrop-filter:blur(10px);transition:transform .3s,box-shadow .3s}
.card:hover{transform:translateY(-4px);box-shadow:0 12px 40px rgba(0,0,0,.4)}
.card-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}
.code{font-weight:bold;color:#fff}.rating{padding:4px 10px;border-radius:12px;font-size:12px;font-weight:bold}
.name{color:#aaa;font-size:14px;margin-bottom:8px}
.price{font-size:28px;font-weight:bold;color:#fff;margin-bottom:12px}
.bar{height:6px;background:rgba(255,255,255,.1);border-radius:3px;overflow:hidden;margin-bottom:12px}
.fill{height:100%;border-radius:3px;transition:width 1s}
.info{display:flex;justify-content:space-between;font-size:12px;color:#aaa;margin-bottom:8px}
.note{font-size:12px;color:#888;font-style:italic}
</style>"""

macro_html = "".join(f'<div class="mitem"><div class="label">{k}</div><div class="val">{v}</div></div>' for k, v in macro.items())
cards_html = "".join(stock_card(s) for s in stocks)
news_html = news_section()

html = f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>股票篩選器</title>
{css}
</head>
<body>
<div class="container">
<h1>📊 智能股票篩選器</h1>
<div class="sub">最後更新：{datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
<div class="macro">{macro_html}</div>
<div class="season-bar"><span>🗓️ 季節：<strong>{season}</strong></span><span class="pos">建議倉位：{position}</span></div>
{news_html}
<div class="grid">{cards_html}</div>
</div>
</body>
</html>"""
# 將 News Section 加落 HTML
html += generate_news_html(news_data)

with open("report.html", "w", encoding="utf-8") as f:
    f.write(html)
print("report.html generated!")
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

# 輸出到頁面（假設你個程式用 print 或寫入 html 檔）

