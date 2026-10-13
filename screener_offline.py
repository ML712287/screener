import os
import json
from pathlib import Path

# ========== 讀取 stock_db ==========
try:
    from stock_db import STOCK_DB
except ImportError:
    STOCK_DB = []

# ========== 宏觀數據（手動 update 時一併改） ==========
MACRO = {
    "us_cpi": 2.5,
    "us_pmi": 54.9,
    "us_10y": 5.19,
    "cn_pmi": 50.6,
    "season": "秋季（偏防禦）",
    "season_class": "season-autumn",
    "alloc": "高息/公用/電訊 35% | 債券 25% | 黃金 15% | 成長 10% | 現金 15%"
}

# ========== HTML 頭部（CSS 樣式全喺呢度） ==========
HTML_HEADER = """
<!DOCTYPE html>
<html lang="zh-HK">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>📊 股票篩選器 | Stock Screener</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: 'Inter', 'Microsoft JhengHei', sans-serif;
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    min-height: 100vh;
    padding: 20px;
    color: #e0e0e0;
}
.container { max-width: 1440px; margin: 0 auto; }

/* 標題區 */
.header {
    text-align: center;
    margin-bottom: 30px;
    padding: 35px 30px 30px;
    background: rgba(255,255,255,0.05);
    border-radius: 24px;
    backdrop-filter: blur(15px);
    border: 1px solid rgba(255,255,255,0.1);
    box-shadow: 0 8px 32px rgba(0,0,0,0.35);
}
.header h1 {
    font-size: 2.4em;
    font-weight: 700;
    background: linear-gradient(90deg, #00d2ff, #3a7bd5, #00d2ff);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shine 3s linear infinite;
    margin-bottom: 8px;
}
@keyframes shine { to { background-position: 200% center; } }
.header .subtitle { font-size: 1em; color: #999; }

/* 宏觀數據欄 */
.macro-bar {
    display: flex;
    flex-wrap: wrap;
    gap: 14px;
    justify-content: center;
    margin-bottom: 25px;
}
.macro-item {
    background: rgba(255,255,255,0.07);
    padding: 14px 22px;
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.12);
    text-align: center;
    min-width: 130px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}
.macro-item .label { font-size: 0.8em; color: #aaa; margin-bottom: 5px; }
.macro-item .value { font-size: 1.25em; font-weight: 600; color: #fff; }
.season-badge {
    display: inline-block;
    padding: 10px 28px;
    border-radius: 25px;
    font-weight: 700;
    font-size: 1.15em;
    margin-top: 18px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}
.season-spring { background: linear-gradient(135deg, #56ab2f, #a8e063); color: #fff; }
.season-summer { background: linear-gradient(135deg, #f12711, #f5af19); color: #fff; }
.season-autumn { background: linear-gradient(135deg, #8E2DE2, #4A00E0); color: #fff; }
.season-winter { background: linear-gradient(135deg, #00d2ff, #3a7bd5); color: #fff; }
.alloc-text { margin-top: 12px; font-size: 0.95em; color: #ccc; }

/* ===== 新聞區 ===== */
.news-section { margin: 28px 0; }
.news-title { font-size: 1.3em; font-weight: 700; color: #fff; margin-bottom: 12px; }
.video-win {
    position: relative; width: 100%; aspect-ratio: 16/9; background: #000;
    border-radius: 16px; overflow: hidden;
    border: 1px solid rgba(255,255,255,0.12);
    box-shadow: 0 8px 25px rgba(0,0,0,0.35);
}
.video-win iframe { position: absolute; inset: 0; width: 100%; height: 100%; border: 0; }
.news-tabs { display: flex; gap: 10px; margin-top: 10px; flex-wrap: wrap; }
.news-tabs button {
    background: rgba(255,255,255,0.08); color: #cbd5e1;
    border: 1px solid rgba(255,255,255,0.15);
    padding: 6px 14px; border-radius: 10px; cursor: pointer; transition: all 0.2s;
}
.news-tabs button:hover { background: rgba(255,255,255,0.15); }
.news-tabs button.active { background: linear-gradient(135deg, #00d2ff, #3a7bd5); color: #fff; }

/* 卡片網格 */
.grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(370px, 1fr));
    gap: 22px;
}

/* 股票卡片 */
.card {
    background: linear-gradient(145deg, rgba(255,255,255,0.09), rgba(255,255,255,0.03));
    border-radius: 18px;
    padding: 22px;
    border: 1px solid rgba(255,255,255,0.12);
    box-shadow: 0 8px 25px rgba(0,0,0,0.25);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}
.card:hover {
    transform: translateY(-6px);
    box-shadow: 0 18px 45px rgba(0,0,0,0.45);
    border-color: rgba(255,255,255,0.28);
}
.card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 4px;
}
.card-A::before { background: linear-gradient(90deg, #00b09b, #96c93d); }
.card-B::before { background: linear-gradient(90deg, #2193b0, #6dd5ed); }
.card-C::before { background: linear-gradient(90deg, #f7971e, #ffd200); }
.card-D::before { background: linear-gradient(90deg, #eb3349, #f45c43); }

/* 卡片內容 */
.card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 14px;
}
.card-title { font-size: 1.25em; font-weight: 700; color: #fff; }
.card-symbol { font-size: 0.82em; color: #999; margin-top: 3px; }
.rating {
    padding: 5px 14px;
    border-radius: 10px;
    font-weight: 700;
    font-size: 0.9em;
    box-shadow: 0 2px 10px rgba(0,0,0,0.2);
}
.rating-A { background: linear-gradient(135deg, #00b09b, #96c93d); color: #fff; }
.rating-B { background: linear-gradient(135deg, #2193b0, #6dd5ed); color: #fff; }
.rating-C { background: linear-gradient(135deg, #f7971e, #ffd200); color: #333; }
.rating-D { background: linear-gradient(135deg, #eb3349, #f45c43); color: #fff; }

.price-row {
    display: flex;
    align-items: baseline;
    gap: 12px;
    margin-bottom: 14px;
}
.price { font-size: 1.9em; font-weight: 700; color: #fff; }
.pe-yield { font-size: 0.88em; color: #aaa; }

.data-row {
    display: flex;
    justify-content: space-between;
    padding: 7px 0;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    font-size: 0.88em;
}
.data-label { color: #999; }
.data-value { color: #e0e0e0; font-weight: 500; }

/* 水位條 */
.water-bar {
    height: 10px;
    background: rgba(255,255,255,0.1);
    border-radius: 5px;
    margin: 12px 0 8px;
    overflow: hidden;
}
.water-fill { height: 100%; border-radius: 5px; transition: width 0.6s ease; }
.water-low { background: linear-gradient(90deg, #00b09b, #96c93d); }
.water-mid { background: linear-gradient(90deg, #f7971e, #ffd200); }
.water-high { background: linear-gradient(90deg, #eb3349, #f45c43); }

/* 入貨位區塊 */
.entry-box {
    margin-top: 14px;
    padding: 14px;
    background: rgba(0,0,0,0.25);
    border-radius: 12px;
    border-left: 4px solid #00d2ff;
}
.entry-label { font-size: 0.78em; color: #999; margin-bottom: 4px; }
.entry-value { font-size: 1.05em; color: #00d2ff; font-weight: 600; }

/* 評語 */
.comment {
    margin-top: 12px;
    padding: 10px 14px;
    background: rgba(255,255,255,0.05);
    border-radius: 8px;
    font-size: 0.84em;
    color: #bbb;
    line-height: 1.5;
}

@media (max-width: 768px) {
    .grid { grid-template-columns: 1fr; }
    .header h1 { font-size: 1.6em; }
    .news-tabs { justify-content: center; }
}
</style>
</head>
<body>
<div class="container">
"""

HTML_FOOTER = """
</div>
</body>
</html>
"""

# ========== 新聞區 HTML 生成 ==========
def news_section_html():
    p = Path(__file__).resolve().parent / "news.json"
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return ""
    flat = [v["id"] for cat in ("us", "cn", "asia") for v in data.get(cat, [])]
    if not flat:
        return ""
    alljs = "".join(f'vids.push("{i}");' for i in flat)
    us = json.dumps([v["id"] for v in data.get("us", [])], ensure_ascii=False)
    cn = json.dumps([v["id"] for v in data.get("cn", [])], ensure_ascii=False)
    asia = json.dumps([v["id"] for v in data.get("asia", [])], ensure_ascii=False)
    return f'''
<div class="news-section">
  <div class="news-title">📺 國際財經新聞（美／中／亞自動輪播·非直播）</div>
  <div class="video-win"><iframe id="newsFrame" src="https://www.youtube-nocookie.com/embed/{flat[0]}?rel=0&modestbranding=1" title="財經新聞" allow="accelerometer;autoplay;clipboard-write;encrypted-media;gyroscope;picture-in-picture" allowfullscreen loading="lazy"></iframe></div>
  <div class="news-tabs">
    <button onclick="setAll()" class="active">🌐 全部輪播</button>
    <button onclick="setList({us})">🇺🇸 只美國</button>
    <button onclick="setList({cn})">🇨🇳 只中國</button>
    <button onclick="setList({asia})">🌏 只亞洲</button>
  </div>
</div>
<script>
var vids=[];{alljs}
var fi=0,timer=null;
function play(i){{document.getElementById('newsFrame').src='https://www.youtube-nocookie.com/embed/'+vids[i]+'?rel=0&modestbranding=1';}}
function next(){{fi=(fi+1)%vids.length;play(fi);}}
function setAll(){{clearInterval(timer);if(!vids.length)return;fi=0;play(0);timer=setInterval(next,60000);}}
function setList(arr){{clearInterval(timer);vids=arr||[];if(!vids.length)return;fi=0;play(0);timer=setInterval(next,60000);}}
if(vids.length){{timer=setInterval(next,60000);}}
</script>
'''

# ========== 評分邏輯 ==========
def score_stock(s):
    score = 0
    try:
        pe = float(s.get('pe', 99))
        if pe > 0 and pe < 12: score += 3
        elif pe < 18: score += 2
        elif pe < 25: score += 1

        dy = float(s.get('div_yield', 0))
        if dy >= 5: score += 3
        elif dy >= 3.5: score += 2
        elif dy >= 2: score += 1

        roe = float(s.get('roe', 0))
        if roe >= 15: score += 2
        elif roe >= 10: score += 1

        debt = float(s.get('debt', 50))
        if debt < 30: score += 2
        elif debt < 50: score += 1
    except:
        pass
    return score

def get_rating(score):
    if score >= 9: return "🟢 A", "A"
    elif score >= 6: return "🔵 B", "B"
    elif score >= 3: return "🟡 C", "C"
    else: return "🔴 D", "D"

# ========== 入貨位計算 ==========
def calc_entry(s):
    try:
        price = float(s.get('price', 0))
        pe = float(s.get('pe', 0))
        dy = float(s.get('div_yield', 0))
        high = s.get('week52high')
        low = s.get('week52low')

        if high and low and float(high) > 0 and float(low) > 0:
            h, l = float(high), float(low)
            mid = (h + l) / 2
            entry_low = round(l * 1.02, 2)
            entry_high = round(mid * 0.98, 2)
            water_pct = round((price - l) / (h - l) * 100, 1) if h > l else 50
            return entry_low, entry_high, water_pct, True

        if pe > 0 and price > 0:
            if pe > 25 or dy < 2:
                target = round(price * 0.84, 2)
                return target, round(price * 0.90, 2), 82, False
            elif dy >= 4:
                return round(price * 0.92, 2), round(price * 1.05, 2), 55, False
            else:
                return round(price * 0.90, 2), round(price * 1.02, 2), 60, False
    except:
        pass
    return None, None, 50, False

# ========== 生成卡片 HTML ==========
def card_html(s):
    score = score_stock(s)
    rating_text, rating_class = get_rating(score)
    entry_low, entry_high, water_pct, is_real = calc_entry(s)

    if water_pct < 40: wc, wlabel = "water-low", "偏低（接近買入區）"
    elif water_pct < 75: wc, wlabel = "water-mid", "中等"
    else: wc, wlabel = "water-high", "偏高（等回調）"

    entry_html = ""
    if entry_low and entry_high:
        src_label = "（52週真實）" if is_real else "（估算）"
        entry_html = f"""
        <div class="entry-box">
            <div class="entry-label">📍 建議入貨區間 {src_label}</div>
            <div class="entry-value">{entry_low} - {entry_high}</div>
            <div class="water-bar">
                <div class="water-fill {wc}" style="width:{min(water_pct, 100)}%"></div>
            </div>
            <div class="entry-label" style="margin-top:4px">💧 現價水位：{water_pct}% — {wlabel}</div>
        </div>
        """

    comment_html = f'<div class="comment">💬 {s.get("comment", "")}</div>' if s.get("comment") else ""

    return f"""
    <div class="card card-{rating_class}">
        <div class="card-header">
            <div>
                <div class="card-title">{s.get('name', 'N/A')}</div>
                <div class="card-symbol">{s.get('symbol', 'N/A')}</div>
            </div>
            <div class="rating rating-{rating_class}">{rating_text}</div>
        </div>
        <div class="price-row">
            <span class="price">{s.get('price', 'N/A')}</span>
            <span class="pe-yield">PE: {s.get('pe', 'N/A')} | 息率: {s.get('div_yield', 'N/A')}%</span>
        </div>
        <div class="data-row"><span class="data-label">EPS</span><span class="data-value">{s.get('eps', 'N/A')}</span></div>
        <div class="data-row"><span class="data-label">PB</span><span class="data-value">{s.get('pb', 'N/A')}</span></div>
        <div class="data-row"><span class="data-label">Margin</span><span class="data-value">{s.get('margin', 'N/A')}%</span></div>
        <div class="data-row"><span class="data-label">ROE</span><span class="data-value">{s.get('roe', 'N/A')}%</span></div>
        <div class="data-row"><span class="data-label">Debt</span><span class="data-value">{s.get('debt', 'N/A')}%</span></div>
        <div class="data-row"><span class="data-label">52週區間</span><span class="data-value">{s.get('week52low', 'N/A')} - {s.get('week52high', 'N/A')}</span></div>
        {entry_html}
        {comment_html}
    </div>
    """

# ========== 主程式 ==========
def main():
    # 宏觀欄 HTML
    macro_html = f"""
    <div class="header">
        <h1>📊 智能股票篩選器</h1>
        <div class="subtitle">Offline Screener · 最後更新：2026-10-13</div>
        <div class="macro-bar">
            <div class="macro-item"><div class="label">🇺🇸 美國 CPI</div><div class="value">{MACRO['us_cpi']}%</div></div>
            <div class="macro-item"><div class="label">🇺🇸 ISM PMI</div><div class="value">{MACRO['us_pmi']}</div></div>
            <div class="macro-item"><div class="label">🇺🇸 10年債</div><div class="value">{MACRO['us_10y']}%</div></div>
            <div class="macro-item"><div class="label">🇨🇳 中國 PMI</div><div class="value">{MACRO['cn_pmi']}</div></div>
        </div>
        <div class="season-badge {MACRO['season_class']}">🌤️ 當前投資季節：{MACRO['season']}</div>
        <div class="alloc-text">📋 建議倉位：{MACRO['alloc']}</div>
    </div>
    """

    # 生成所有卡片
    cards = []
    for s in STOCK_DB:
        try:
            cards.append(card_html(s))
        except Exception as e:
            print(f"[WARN] {s.get('symbol', '?')} 跳過: {e}")

    # 組合完整 HTML（順序：Header → Macro → News → Grid → Footer）
    news_html = news_section_html()
    html = (HTML_HEADER
            + macro_html
            + news_html
            + '<div class="grid">' + "\n".join(cards) + '</div>'
            + HTML_FOOTER)

    # 輸出路徑
    base_path = Path(__file__).resolve().parent
    out = base_path / "report.html"
    os.makedirs(out.parent, exist_ok=True)

    with open(out, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ report.html 已生成：{out}")

if __name__ == "__main__":
    main()
