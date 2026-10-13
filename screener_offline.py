import time

news_data = {
    "测试": [{"title": "测试片：Rick Astley", "id": "dQw4w9WgXcQ"}]
}

macro = {"恒指": "18000", "纳指": "15000"}
stocks = [{"code": "00700", "name": "腾讯"}]
season = "秋季"
position = "50%"

def generate_news_html(news_data):
    html = '<div class="news-sec"><h2>News 区测试</h2>'
    for region, items in news_data.items():
        html += f'<div id="nv-{region}" style="display:block;">'
        html += f'<div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;background:#000;border-radius:12px;"><iframe id="player-{region}" src="https://www.youtube.com/embed/{items[0]["id"]}" style="position:absolute;top:0;left:0;width:100%;height:100%;border:0;" allowfullscreen></iframe></div>'
        html += f'<div style="margin-top:10px;">'
        for v in items:
            html += f'<div style="padding:10px;background:#333;border-radius:8px;margin-bottom:5px;cursor:pointer;">{v["title"]}</div>'
        html += '</div></div>'
    html += '</div>'
    return html

css = """
<style>
body{background:#111;color:#fff;font-family:sans-serif;margin:0;padding:20px}
.container{max-width:800px;margin:0 auto}
.news-sec{padding:20px;background:#222;border-radius:12px;margin-top:20px}
</style>
"""

macro_html = "".join(f'<div style="background:#222;padding:10px 15px;border-radius:8px;text-align:center;display:inline-block;margin-right:10px;"><div style="color:#aaa;font-size:12px;">{k}</div><div style="font-size:20px;font-weight:bold;color:#4fc3f7;">{v}</div></div>' for k, v in macro.items())
cards_html = "".join(f'<div style="background:#222;padding:15px;border-radius:10px;min-width:120px;text-align:center;display:inline-block;margin-right:10px;"><h3>{s["code"]}</h3><p>{s["name"]}</p></div>' for s in stocks)
news_html = generate_news_html(news_data)

current_time = time.strftime('%Y-%m-%d %H:%M')

html = f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<title>股票筛选器</title>
{css}
</head>
<body>
<div class="container">
<h1>智能股票筛选器</h1>
<div style="color:#aaa;margin-bottom:20px;">最后更新：{current_time}</div>
<div style="margin-bottom:20px;">{macro_html}</div>
<div style="background:#222;padding:10px 15px;border-radius:8px;margin-bottom:20px;display:flex;justify-content:space-between;">
<span>季节：{season}</span><span>建议仓位：{position}</span>
</div>
{news_html}
<div style="margin-top:20px;">{cards_html}</div>
</div>
</body>
</html>
"""

with open("report.html", "w", encoding="utf-8") as f:
    f.write(html)
print("report.html generated!")
