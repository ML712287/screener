import time

# ===== 数据 =====
macro = {
    "恒指": "18,200",
    "纳指": "15,120", 
    "S&P 500": "4,580",
    "CPI": "2.4%",
    "PMI": "49.8"
}

stocks = [
    {"code": "00700", "name": "腾讯控股", "price": "328.40", "pe": "14.2", "change": "+1.2%"},
    {"code": "09988", "name": "阿里巴巴", "price": "78.50", "pe": "12.8", "change": "-0.8%"},
    {"code": "03690", "name": "美团", "price": "112.60", "pe": "22.1", "change": "+2.3%"},
    {"code": "01810", "name": "小米集团", "price": "18.24", "pe": "28.5", "change": "+0.5%"},
    {"code": "02318", "name": "中国平安", "price": "42.80", "pe": "8.4", "change": "-1.1%"},
    {"code": "00941", "name": "中国移动", "price": "68.90", "pe": "10.2", "change": "+0.3%"},
    {"code": "00388", "name": "香港交易所", "price": "265.00", "pe": "31.6", "change": "+0.8%"},
    {"code": "01299", "name": "友邦保险", "price": "58.40", "pe": "18.9", "change": "-0.4%"},
    {"code": "02628", "name": "中国人寿", "price": "12.68", "pe": "6.2", "change": "+1.5%"},
    {"code": "03988", "name": "中国银行", "price": "3.42", "pe": "4.1", "change": "0.0%"},
]

season = "秋季"
position = "50%"

# ===== HTML 生成 =====
macro_html = ""
for k, v in macro.items():
    macro_html += f'<span class="macro-badge">{k}<b>{v}</b></span>'

stocks_html = ""
for s in stocks:
    color = "#4caf50" if s["change"].startswith("+") else "#f44336" if s["change"].startswith("-") else "#aaa"
    stocks_html += f'''
    <div class="stock-card" data-code="{s["code"]}" data-name="{s["name"]}">
        <div class="stock-code">{s["code"]}</div>
        <div class="stock-name">{s["name"]}</div>
        <div class="stock-price">${s["price"]}</div>
        <div class="stock-meta">PE {s["pe"]} <span style="color:{color}">{s["change"]}</span></div>
    </div>'''

current_time = time.strftime('%Y-%m-%d %H:%M')

html = f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<title>股票筛选器</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
    background: 
        radial-gradient(circle at 20% 50%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
        radial-gradient(circle at 80% 80%, rgba(255, 119, 198, 0.15) 0%, transparent 50%),
        radial-gradient(circle at 40% 20%, rgba(120, 219, 255, 0.15) 0%, transparent 50%),
        #0a0e1a;
    color: #e0e0e0;
    font-family: 'Segoe UI', system-ui, sans-serif;
    min-height: 100vh;
    padding: 16px;
}}
.container {{
    max-width: 960px;
    margin: 0 auto;
}}
h1 {{
    font-size: 1.6em;
    font-weight: 700;
    background: linear-gradient(135deg, #00d2ff, #7b61ff, #ff6ec4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 4px;
}}
.subtitle {{
    font-size: 0.8em;
    color: #666;
    margin-bottom: 16px;
}}
.macro-row {{
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 14px;
}}
.macro-badge {{
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.1);
    backdrop-filter: blur(10px);
    border-radius: 10px;
    padding: 8px 14px;
    font-size: 0.78em;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}}
.macro-badge b {{
    display: block;
    font-size: 1.15em;
    background: linear-gradient(135deg, #00d2ff, #7b61ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-top: 2px;
}}
.info-row {{
    display: flex;
    gap: 8px;
    margin-bottom: 14px;
}}
.info-tag {{
    background: linear-gradient(135deg, rgba(0,210,255,0.15), rgba(123,97,255,0.15));
    border: 1px solid rgba(0,210,255,0.3);
    border-radius: 10px;
    padding: 8px 16px;
    font-size: 0.82em;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}}
.search-box {{
    width: 100%;
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 12px;
    padding: 10px 16px;
    color: #fff;
    font-size: 0.9em;
    margin-bottom: 14px;
    outline: none;
    backdrop-filter: blur(10px);
    box-shadow: inset 0 2px 8px rgba(0,0,0,0.3);
}}
.search-box::placeholder {{ color: #555; }}
.search-box:focus {{
    border-color: rgba(0,210,255,0.5);
    box-shadow: 0 0 0 3px rgba(0,210,255,0.1), inset 0 2px 8px rgba(0,0,0,0.3);
}}
.stock-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 8px;
}}
.stock-card {{
    background: linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03));
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px;
    padding: 10px 12px;
    cursor: pointer;
    transition: all 0.2s;
    box-shadow: 0 4px 12px rgba(0,0,0,0.25);
}}
.stock-card:hover {{
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(0,210,255,0.2);
    border-color: rgba(0,210,255,0.4);
}}
.stock-code {{
    font-size: 0.72em;
    color: #888;
    margin-bottom: 2px;
}}
.stock-name {{
    font-size: 0.88em;
    font-weight: 600;
    margin-bottom: 4px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}
.stock-price {{
    font-size: 1.05em;
    font-weight: 700;
    background: linear-gradient(135deg, #00d2ff, #7b61ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}
.stock-meta {{
    font-size: 0.72em;
    color: #666;
    margin-top: 2px;
}}
.no-result {{
    text-align: center;
    padding: 30px;
    color: #555;
    font-size: 0.9em;
    display: none;
}}
</style>
</head>
<body>
<div class="container">
    <h1>📊 智能股票筛选器</h1>
    <div class="subtitle">最后更新：{current_time}</div>

    <div class="macro-row">{macro_html}</div>

    <div class="info-row">
        <span class="info-tag">🌤️ 季节：{season}</span>
        <span class="info-tag">💼 仓位：{position}</span>
    </div>

    <input class="search-box" type="text" placeholder="🔍 输入股票代码或名称搜尋（例：00700 / 腾讯）" oninput="filterStocks(this.value)">

    <div class="stock-grid" id="stockGrid">{stocks_html}</div>
    <div class="no-result" id="noResult">冇找到匹配嘅股票 😢</div>
</div>

<script>
function filterStocks(keyword) {{
    keyword = keyword.toLowerCase().trim();
    const cards = document.querySelectorAll('.stock-card');
    const noResult = document.getElementById('noResult');
    let visible = 0;

    cards.forEach(card => {{
        const code = card.dataset.code.toLowerCase();
        const name = card.dataset.name.toLowerCase();
        if (code.includes(keyword) || name.includes(keyword)) {{
            card.style.display = '';
            visible++;
        }} else {{
            card.style.display = 'none';
        }}
    }});

    noResult.style.display = visible === 0 ? 'block' : 'none';
}}
</script>
</body>
</html>
"""

with open("report.html", "w", encoding="utf-8") as f:
    f.write(html)
print("report.html generated!")
