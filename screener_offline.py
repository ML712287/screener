import time

news_data = {
    "测试区": [{"title": "Rick Astley - Never Gonna Give You Up", "id": "dQw4w9WgXcQ"}]
}

def generate_news_html(news_data):
    html = '<div class="news-section"><h2>📰 新闻与影片</h2>'
    for region, items in news_data.items():
        html += f'<div class="video-win"><iframe src="https://www.youtube.com/embed/{items[0]["id"]}" allowfullscreen></iframe></div>'
        for v in items:
            html += f'<p>{v["title"]}</p>'
    html += '</div>'
    return html

css = """
<style>
body{background:#111;color:#fff;font-family:sans-serif;padding:20px}
.news-section{margin:20px 0;padding:20px;background:#222;border-radius:10px}
.video-win{position:relative;width:100%;aspect-ratio:16/9;background:#000;border-radius:8px;overflow:hidden}
.video-win iframe{width:100%;height:100%;border:0}
</style>
"""

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
<h1>📊 智能股票筛选器</h1>
<div>最后更新：{current_time}</div>
{news_html}
</body>
</html>
"""

with open("report.html", "w", encoding="utf-8") as f:
    f.write(html)
print("report.html generated!")
