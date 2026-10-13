# -*- coding: utf-8 -*-
"""
Yuanbao Capital · 智能篩選儀表板（離線版）
用真實數據庫直接生成 HTML，唔需要 call API，可即時測試。
正式用請用 screener.py（會 call Yahoo API 攞最新數據）。
"""
import sys
import datetime
from stock_db import STOCK_DB

# ============================================================
#  宏觀數據（最新）
# ============================================================
MACRO = {
    "us_gdp": 3.8, "us_cpi": 2.9, "us_unemployment": 4.3,
    "cn_gdp": 5.2, "cn_cpi": 0.6, "cn_ppi": -2.5,
}

def judge_season(m):
    score = 0
    if m["us_gdp"] > 3: score += 1
    if m["us_gdp"] < 1.5: score -= 1
    if m["us_cpi"] > 3: score += 1
    if m["us_cpi"] < 2: score -= 1
    if m["us_unemployment"] > 4.5: score -= 1
    if m["cn_cpi"] < 1 and m["cn_ppi"] < 0: score -= 0.5
    if score >= 1.5: return "夏", "夏", score
    if score >= 0: return "秋", "秋/冬", score
    if score >= -1: return "秋/冬", "冬", score
    return "冬", "冬", score

SEASON_ADVICE = {
    "春": {"name":"春季 · 復甦期","desc":"經濟由衰退轉復甦，通脹低，利率見底。","do":"增持成長股、科技、周期；減持防守股、長債。",
      "alloc":{"成長股/科技":35,"周期股":20,"高息/公用":20,"債券/現金":15,"黃金":10},"buy":["科技成長","生物科技","周期股"],"avoid":["長債","防守股"]},
    "夏": {"name":"夏季 · 過熱期","desc":"經濟過熱，通脹升，利率升。","do":"增持資源、商品、現金；減持高估值科技。",
      "alloc":{"資源/商品":30,"現金":20,"成長股":20,"高息/公用":15,"債券":15},"buy":["資源股","黃金","商品","能源"],"avoid":["高估值科技","長債"]},
    "秋": {"name":"秋季 · 放緩期","desc":"經濟放緩，通脹降，利率開始降。","do":"增持高息股、公用、電訊、長債；減持資源。",
      "alloc":{"高息/公用/電訊":35,"債券/長債":25,"黃金/資源":15,"成長股":10,"現金":15},"buy":["高息股","公用","電訊","黃金","長債"],"avoid":["高估值科技","半導體軟件"]},
    "冬": {"name":"冬季 · 衰退期","desc":"經濟衰退，通脹低，利率大跌。","do":"增持長債、國債、現金；清倉大部分股票。",
      "alloc":{"債券/長債":40,"現金":20,"黃金":15,"防守股":15,"股票":10},"buy":["長債","國債","現金","防守"],"avoid":["大部分股票"]},
    "秋/冬": {"name":"深秋/初冬","desc":"中國深秋初冬，美股夏末秋初。","do":"防守 + 高息 + 對沖。",
      "alloc":{"高息/公用/電訊":30,"債券/長債":25,"黃金/資源":15,"成長股":10,"現金":20},"buy":["高息股","公用","電訊","黃金"],"avoid":["高估值科技"]},
}

# 行業分類（股票代號 → 行業）
# 用途：1) 決定季節匹配 2) 行業化框架門檻
INDUSTRY_MAP = {
    # 公用/電力/水務/電訊/基建 → 秋
    "utility": ["0002.HK","0003.HK","0006.HK","0836.HK","0855.HK","01038.HK","0836.HK",
                "DUK","EIX","SRE","NEE","SO","AES","NEP","BEP","CWEN","AY","TER"],
    # 能源/資源/油氣/礦業/黃金 → 夏
    "resource": ["02899.HK","0857.HK","0883.HK","0960.HK","601899.SS","601857.SS","600028.SS",
                 "601088.SS","1088.HK",
                 "CVX","XOM","GOLD","NEM","FNV","CCJ","NXT","VRT","RCL","CCL"],
    # 金融/銀行/保險 → 秋（高息防守）
    "finance": ["0939.HK","2318.HK","2328.HK","0019.HK",
                "600036.SS","601318.SS","601988.SS","601398.SS","601628.SS","601601.SS",
                "601328.SS","601939.SS","601166.SS","601818.SS","601933.SS","600030.SS","600000.SS"],
    # 電訊 → 秋
    "telecom": ["0762.HK","0941.HK","02388.HK","0968.HK","CHT","T","VZ","VOD","TMUS","TEF","ORAN"],
    # 消費（高息/防守） → 秋
    "consumer_defensive": ["0001.HK","KO","PEP","MCD","WMT","COST","EL","PG","CL","KMB","HSY","GIS","TAP","CAG"],
    # 消費（成長） → 春
    "consumer_growth": ["6862.HK","2331.HK","6690.HK","000333.SZ","000858.SZ","600519.SS","002714.SZ","VRTX"],
    # 科技/軟件/半導體 → 春
    "tech": ["0700.HK","1024.HK","0981.HK","2382.HK","0285.HK","9988.HK","9866.HK",
             "601138.SS","002475.SZ","000725.SZ","600745.SZ","603501.SS","300408.SZ",
             "AAPL","MSFT","NVDA","GOOGL","AMZN","META","CRM","ADBE","ORCL","NOW","SNOW","AMD","INTC","QCOM","TXN","AVGO","MU","AMAT","LRCX","KLAC","SNPS","CDNS","PANW","CRWD","ZS","OKTA"],
    # 醫藥/生物 → 春（成長）＋ 秋（防守，如JNJ/PFE）
    "pharma_growth": ["1177.HK","2269.HK","300760.SZ","002422.SZ","600276.SS","601216.SS",
                      "LLY","NFLX","ISRG","VRTX","REGN","MRNA","BNTX","SGEN","BIIB","GILD","AMGN","VRTX"],
    "pharma_defensive": ["JNJ","PFE","MRK","ABBV","TMO","DHR","SYK","BSX","MDT","ZBH","ZTS","IQV","VEEV"],
    # 工業/電力設備/軍工 → 春（政策驅動）
    "industrial": ["600406.SS","002179.SZ","300274.SZ","601012.SS","601360.SS","601727.SS","601669.SS","601186.SS","601800.SS",
                   "HD","LOW","CAT","DE","MMM","GE","HON","UPS","FDX","UNP","CSX","NSC","BA","LMT","RTX","NOC","GD","ITW","ETN","PH","ROK"],
}

# 行業 → 適合季節
INDUSTRY_SEASON = {
    "utility": "秋", "finance": "秋", "telecom": "秋", "consumer_defensive": "秋", "pharma_defensive": "秋",
    "resource": "夏",
    "consumer_growth": "春", "tech": "春", "pharma_growth": "春", "industrial": "春",
}

def get_industry(symbol):
    for ind, syms in INDUSTRY_MAP.items():
        if symbol in syms: return ind
    return "other"

def season_fit(symbol, season):
    ind = get_industry(symbol)
    best = INDUSTRY_SEASON.get(ind)
    if not best: return False
    # 精確匹配，或 秋/冬 互通（防守性資產四季通用）
    if best == season: return True
    if best == "秋" and season in ("秋","秋/冬"): return True
    if best == "冬" and season in ("冬",): return True
    return False

# 行業化框架門檻
INDUSTRY_THRESHOLDS = {
    "utility":  {"roe": 8,  "margin": 15},
    "finance":  {"roe": 10, "margin": None},
    "telecom":  {"roe": 8,  "margin": 30},
    "consumer_defensive": {"roe": 15, "margin": 35},
    "consumer_growth":    {"roe": 12, "margin": 20},
    "tech":     {"roe": 12, "margin": 35},
    "pharma_growth":    {"roe": 12, "margin": 55},
    "pharma_defensive": {"roe": 10, "margin": 55},
    "industrial": {"roe": 10, "margin": 18},
    "resource":  {"roe": 8,  "margin": 12},
    "other":     {"roe": 12, "margin": 25},
}

# ============================================================
#  3+2+2 框架
# ============================================================
def pass_framework(s):
    passed, failed = [], []
    ind = get_industry(s["symbol"])
    thr = INDUSTRY_THRESHOLDS.get(ind, INDUSTRY_THRESHOLDS["other"])
    # 3 核心（行業化門檻）
    fcf = s.get("fcf")
    if fcf is not None and fcf > 0: passed.append("fcf_positive")
    else: failed.append("fcf_positive")
    roe = s.get("roe")
    roe_min = thr["roe"]
    if roe is not None and roe > roe_min: passed.append("roe_gt_12")
    else: failed.append("roe_gt_12")
    pe = s.get("pe")
    pb = s.get("pb")
    # 估值：PE<30 且 >0，或 PB<5（公用/金融容許 PB 高啲）
    if (pe and 0 < pe < 35) or (pb and 0 < pb < 6): passed.append("val_quantile_lt_70")
    else: failed.append("val_quantile_lt_70")
    # 2 否定
    veto = True
    payout = s.get("payout")
    if payout and payout > 100: veto = False
    debt = s.get("debt")
    if debt and debt > 80:
        if roe is None or roe < 8: veto = False
    if pe and pe < 0: veto = False
    return {"passed_core":passed,"failed_core":failed,"veto_pass":veto,"pass_all":len(failed)==0 and veto}

def grade_stock(s, fw, season):
    score = 0; tags = []
    if fw["pass_all"]:
        score += 3; tags.append("框架全過")
    else:
        if "roe_gt_12" in fw["passed_core"]: score += 1
        if "fcf_positive" in fw["passed_core"]: score += 1
    if season_fit(s["symbol"], season):
        score += 2; tags.append("季節匹配")
    margin = s.get("margin")
    if margin and margin > 40: score += 1; tags.append("高毛利")
    div = s.get("div_yield")
    if div and div > 4: score += 1; tags.append("高息")
    roe = s.get("roe")
    if roe and roe > 20: score += 1; tags.append("高ROE")

    if score >= 6: grade, color = "A", "🟢"
    elif score >= 4: grade, color = "B", "🟡"
    else: grade, color = "C", "🔴"
    return grade, color, score, tags

def get_comment(s, grade, season):
    base = s.get("comment","")
    if grade == "A": return f"強烈推薦：{base} 符合框架 + {season}季節核心。"
    if grade == "B": return f"可考慮：{base} 部分符合，觀望。"
    return f"避開：{base}"

# ============================================================
#  生成 HTML
# ============================================================
def gen_html(results, filtered, season_global, season_cn, score):
    advice = SEASON_ADVICE.get(season_global, SEASON_ADVICE["秋"])
    gen_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    def alloc_bars(alloc):
        return "".join(
            f'<div class="alloc-row"><span class="alloc-label">{k}</span><div class="alloc-bar"><div class="alloc-fill" style="width:{v}%"></div><span class="alloc-pct">{v}%</span></div></div>'
            for k,v in alloc.items())

    n_hk = len([r for r in filtered if r["market_label"]=="港股"])
    n_cn = len([r for r in filtered if r["market_label"]=="A股"])
    n_us = len([r for r in filtered if r["market_label"]=="美股"])
    grade_a = [r for r in filtered if r["grade"]=="A"]
    grade_b = [r for r in filtered if r["grade"]!="A"]
    cards_a = "".join(card(r) for r in grade_a)
    cards_b = "".join(card(r) for r in grade_b)
    if not cards_a: cards_a = '<div class="empty">無股票達到「框架全過 + 季節匹配」。</div>'
    extra = ""
    if cards_b:
        extra = f'<div class="section-title">🟡 觀望：部分符合框架 + {season_global}季節</div><div class="cards">{cards_b}</div>'
    cards = f'<div class="section-title">🟢 推薦：框架全過 + {season_global}季節核心</div><div class="cards">{cards_a}</div>{extra}'
    html = f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>Yuanbao Capital · 智能篩選儀表板</title>
<style>
:root{{--bg:#0f1115;--card:#1a1d24;--gold:#d4a94a;--green:#3fb950;--yellow:#d29922;--red:#f85149;--text:#e6edf3;--sub:#8b949e;--border:#30363d;}}
*{{box-sizing:border-box;margin:0;padding:0;-webkit-tap-highlight-color:transparent;}}
body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang TC","Microsoft YaHei",sans-serif;background:var(--bg);color:var(--text);line-height:1.5;padding-bottom:env(safe-area-inset-bottom);}}
.wrap{{max-width:960px;margin:0 auto;padding:16px;}}
header{{text-align:center;padding:20px 0 16px;border-bottom:1px solid var(--border);margin-bottom:16px;}}
.logo{{font-size:22px;font-weight:800;color:var(--gold);letter-spacing:1px;}}
.logo span{{color:var(--text);font-weight:400;font-size:14px;display:block;margin-top:4px;}}
.season-box{{background:linear-gradient(135deg,#1f2430,#161a21);border:1px solid var(--gold);border-radius:14px;padding:16px;margin-bottom:16px;}}
.season-box h2{{font-size:18px;color:var(--gold);margin-bottom:8px;}}
.season-box .desc{{color:var(--sub);font-size:14px;margin-bottom:10px;}}
.season-box .do{{color:var(--green);font-size:15px;font-weight:600;}}
.macro{{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:12px;}}
.macro .m{{background:var(--card);border-radius:8px;padding:8px;text-align:center;}}
.macro .m .l{{font-size:11px;color:var(--sub);}}
.macro .m .v{{font-size:16px;font-weight:700;color:var(--text);}}
.alloc-box{{background:var(--card);border-radius:14px;padding:16px;margin-bottom:16px;}}
.alloc-box h3{{font-size:16px;margin-bottom:12px;color:var(--gold);}}
.alloc-row{{display:flex;align-items:center;margin-bottom:8px;}}
.alloc-label{{width:110px;font-size:13px;color:var(--sub);flex-shrink:0;}}
.alloc-bar{{flex:1;background:#0d1117;border-radius:6px;height:22px;position:relative;overflow:hidden;}}
.alloc-fill{{height:100%;background:linear-gradient(90deg,var(--gold),#e8c87a);border-radius:6px;}}
.alloc-pct{{position:absolute;right:6px;top:2px;font-size:12px;color:var(--text);}}
.summary{{display:flex;gap:10px;margin-bottom:16px;flex-wrap:wrap;}}
.stat{{flex:1;min-width:90px;background:var(--card);border-radius:10px;padding:12px;text-align:center;}}
.stat .num{{font-size:24px;font-weight:800;color:var(--gold);}}
.stat .lbl{{font-size:12px;color:var(--sub);}}
.section-title{{font-size:17px;font-weight:700;margin:20px 0 12px;color:var(--text);}}
.cards{{display:flex;flex-direction:column;gap:12px;}}
.card{{background:var(--card);border-radius:12px;padding:14px;border-left:4px solid var(--border);}}
.card.grade-A{{border-left-color:var(--green);}}
.card.grade-B{{border-left-color:var(--yellow);}}
.card.grade-C{{border-left-color:var(--red);}}
.card-head{{display:flex;justify-content:space-between;align-items:flex-start;gap:8px;margin-bottom:10px;}}
.card-title{{display:flex;flex-wrap:wrap;align-items:center;gap:6px;}}
.market-badge{{font-size:11px;padding:2px 6px;border-radius:4px;color:#fff;}}
.market-badge.港股{{background:#d32f2f;}}
.market-badge.A股{{background:#c62828;}}
.market-badge.美股{{background:#1565c0;}}
.sym{{font-weight:700;font-size:15px;}}
.name{{font-size:12px;color:var(--sub);width:100%;}}
.card-grade{{font-size:18px;font-weight:800;flex-shrink:0;}}
.card-metrics{{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin-bottom:10px;}}
.metric{{background:#0d1117;border-radius:6px;padding:6px;text-align:center;}}
.m-label{{display:block;font-size:10px;color:var(--sub);}}
.m-val{{display:block;font-size:13px;font-weight:600;}}
.card-fw{{font-size:12px;color:var(--sub);margin-bottom:8px;}}
.card-tags{{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:8px;}}
.tag{{font-size:11px;background:#21262d;color:var(--gold);padding:2px 8px;border-radius:10px;}}
.card-comment{{font-size:13px;color:var(--text);background:#0d1117;border-radius:8px;padding:8px;}}
.entry-block{{background:#0d1117;border:1px solid var(--border);border-left:3px solid var(--gold);border-radius:8px;padding:10px 12px;margin-bottom:10px;}}
.entry-row{{display:flex;justify-content:space-between;align-items:flex-start;gap:10px;font-size:13px;padding:3px 0;}}
.entry-row + .entry-row{{border-top:1px dashed #21262d;}}
.entry-k{{color:var(--sub);flex-shrink:0;}}
.entry-v{{color:var(--text);font-weight:600;text-align:right;}}
.entry-v.hot{{color:var(--red);}} .entry-v.cool{{color:var(--green);}}
.empty{{text-align:center;color:var(--sub);padding:40px 20px;}}
footer{{text-align:center;color:var(--sub);font-size:11px;padding:24px 0 40px;}}
@media(max-width:480px){{.macro{{grid-template-columns:repeat(2,1fr);}}.alloc-label{{width:80px;font-size:12px;}}}}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <div class="logo">YUANBAO CAPITAL<span>智能股票篩選儀表板 · v3.1</span></div>
  </header>
  <div class="season-box">
    <h2>{advice['name']}</h2>
    <div class="desc">{advice['desc']}</div>
    <div class="do">👉 {advice['do']}</div>
    <div class="macro">
      <div class="m"><div class="l">美國 GDP</div><div class="v">{MACRO['us_gdp']}%</div></div>
      <div class="m"><div class="l">美 CPI</div><div class="v">{MACRO['us_cpi']}%</div></div>
      <div class="m"><div class="l">美失業率</div><div class="v">{MACRO['us_unemployment']}%</div></div>
      <div class="m"><div class="l">中 GDP</div><div class="v">{MACRO['cn_gdp']}%</div></div>
      <div class="m"><div class="l">中 CPI</div><div class="v">{MACRO['cn_cpi']}%</div></div>
      <div class="m"><div class="l">中 PPI</div><div class="v">{MACRO['cn_ppi']}%</div></div>
    </div>
  </div>
  <div class="alloc-box">
    <h3>📊 當前季節建議資產比例</h3>
    {alloc_bars(advice['alloc'])}
  </div>
  <div class="summary">
    <div class="stat"><div class="num">{len(filtered)}</div><div class="lbl">符合條件</div></div>
    <div class="stat"><div class="num">{n_hk}</div><div class="lbl">港股</div></div>
    <div class="stat"><div class="num">{n_cn}</div><div class="lbl">A股</div></div>
    <div class="stat"><div class="num">{n_us}</div><div class="lbl">美股</div></div>
  </div>
  <div class="section-title">🟢 符合「3+2+2」框架 + {season_global}季節嘅股票</div>
  <div class="cards">{cards}</div>
  <footer>
    生成時間：{gen_time} · 宏觀評分：{score} · 離線數據庫模式<br>
    數據來源：Yahoo Finance / 公司年報（離線版） · 僅供參考，不構成投資建議<br>
    ⚠️ 投資有風險，決策需謹慎
  </footer>
</div>
</body>
</html>"""
    return html


def card(r):
        tags = " ".join(f'<span class="tag">{t}</span>' for t in r["tags"])
        fw = r["framework"]
        passed = len(fw["passed_core"])
        fcf_txt = "正" if (r.get("fcf") and r["fcf"]>0) else ("負/無" if r.get("fcf") is not None else "—")
        div_txt = f"{r['div_yield']}%" if r.get("div_yield") else "—"
        price = r.get("price") or 0
        hi = r.get("week52high")
        lo = r.get("week52low")
        if hi and lo and hi > lo and price:
            pos = (price - lo) / (hi - lo) * 100
            pos_txt = f"{pos:.0f}%"
            mid = (hi + lo) / 2
            r_low = round(mid - (hi - lo) * 0.12, 2)
            r_high = round(mid + (hi - lo) * 0.03, 2)
            if r_low < lo:
                r_low = round(lo, 2)
            zone = f"{r_low:.2f} - {r_high:.2f}"
            if pos >= 95:
                timing = f"已破頂（52週高 {hi:.2f}），等回調 5-8% 再入"
            elif pos >= 75:
                timing = f"接近高位（水位 {pos:.0f}%），分兩注：現價半注 + 回調 {r_low:.1f} 加注"
            elif pos >= 40:
                timing = f"水位合理（{pos:.0f}%），可分注買入"
            else:
                timing = f"接近低位（水位 {pos:.0f}%），可較積極建倉"
            water_cls = "hot" if pos >= 75 else "cool"
        else:
            # fallback：冇 52週高低位，用股價 + 行業特性估算
            if price:
                name = (r.get("name") or "").lower()
                sym = (r.get("symbol") or "").upper()
                pe = r.get("pe") or 0
                div = r.get("div_yield") or 0
                # 行業特性：公用/電訊/電力類偏防守，波幅細；消費/醫藥/零售波幅大
                defensive = any(k in name for k in ["electric","power","utility","water","gas","telecom","tele","energy","bank","financial","insurance","reit","estate","property"])
                # 防守型：±8%；增長型：±12%
                rng = 0.08 if defensive else 0.12
                # 估值偏貴（PE 高）時，入貨區間向下移
                pe_expensive = pe > 25
                if pe_expensive:
                    r_low = round(price * (1 - rng * 1.4), 2)
                    r_high = round(price * (1 - rng * 0.2), 2)
                    pos_txt = f"偏高(PE{pe:.0f})"
                    timing = f"估值偏貴，等回調 {int(rng*100*1.4)}% 至 {r_low:.1f} 附近再入"
                    water_cls = "hot"
                else:
                    r_low = round(price * (1 - rng), 2)
                    r_high = round(price * (1 + rng * 0.25), 2)
                    pos_txt = f"中"
                    timing = f"無 52週數據，按估值估算入貨區間（防守型 ±{int(rng*100)}%）"
                    water_cls = "cool"
                zone = f"{r_low:.2f} - {r_high:.2f}（估算）"
            else:
                pos_txt, zone, timing = "—", "—", "無股價數據"
                water_cls = ""
        fw_core = "✅ 全過" if fw["pass_all"] else "⚠️ 部分過"
        fw_veto = "否決✅" if fw["veto_pass"] else "否決❌"
        season_tag = " ｜ 🍂季節匹配" if r["season_fit"] else ""
        return (
        '<div class="card grade-' + r["grade"] + '">'
          '<div class="card-head">'
            '<div class="card-title">'
              '<span class="market-badge ' + r["market_label"] + '">' + r["market_label"] + '</span>'
              '<span class="sym">' + r["symbol"] + '</span>'
              '<span class="name">' + r["name"] + '</span>'
            '</div>'
            '<div class="card-grade">' + r["color"] + ' ' + r["grade"] + '</div>'
          '</div>'
          '<div class="card-metrics">'
            '<div class="metric"><span class="m-label">股價</span><span class="m-val">' + str(r["price"]) + '</span></div>'
            '<div class="metric"><span class="m-label">EPS</span><span class="m-val">' + str(r["eps"]) + '</span></div>'
            '<div class="metric"><span class="m-label">PE</span><span class="m-val">' + str(r["pe"]) + '</span></div>'
            '<div class="metric"><span class="m-label">PB</span><span class="m-val">' + str(r["pb"]) + '</span></div>'
            '<div class="metric"><span class="m-label">息率</span><span class="m-val">' + div_txt + '</span></div>'
            '<div class="metric"><span class="m-label">ROE</span><span class="m-val">' + str(r["roe"]) + '%</span></div>'
            '<div class="metric"><span class="m-label">毛利</span><span class="m-val">' + str(r["margin"]) + '%</span></div>'
            '<div class="metric"><span class="m-label">FCF</span><span class="m-val">' + fcf_txt + '</span></div>'
          '</div>'
          '<div class="card-fw">框架：' + str(passed) + '/3 核心 ' + fw_core + ' ｜ ' + fw_veto + season_tag + '</div>'
          '<div class="card-tags">' + tags + '</div>'
          '<div class="entry-block">'
            '<div class="entry-row"><span class="entry-k">📍 建議入貨區間</span><span class="entry-v">' + zone + '</span></div>'
            '<div class="entry-row"><span class="entry-k">💧 現價水位（52週）</span><span class="entry-v ' + water_cls + '">' + pos_txt + '</span></div>'
            '<div class="entry-row"><span class="entry-k">⏳ 下一入貨時機</span><span class="entry-v">' + timing + '</span></div>'
          '</div>'
          '<div class="card-comment">' + r["comment"] + '</div>'
        '</div>')


def main():
    season_global, season_cn, score = judge_season(MACRO)
    advice = SEASON_ADVICE.get(season_global, SEASON_ADVICE["秋"])
    print(f"當前季節：全球={season_global} ｜ 中國={season_cn} ｜ 評分={score}")
    print(f"建議：{advice['do']}")
    print(f"股票池：{len(STOCK_DB)} 隻")
    results = []
    for s in STOCK_DB:
        fw = pass_framework(s)
        grade, color, gscore, tags = grade_stock(s, fw, season_global)
        if s["symbol"].endswith(".HK"): mkt = "港股"
        elif s["symbol"].endswith((".SS",".SZ")): mkt = "A股"
        else: mkt = "美股"
        results.append({**s, "framework":fw, "grade":grade, "color":color,
                        "score":gscore, "tags":tags, "season_fit":season_fit(s["symbol"], season_global),
                        "market_label":mkt, "comment":get_comment(s, grade, season_global)})
    # 放寬：框架至少過 2/3 核心 + 季節匹配，即視為推薦
    filtered = [r for r in results if r["season_fit"] and len(r["framework"]["passed_core"]) >= 2]
    print(f"符合全部條件（A級）：{len(filtered)} 隻")
    for r in filtered:
        print(f"  {r['color']} [{r['market_label']}] {r['symbol']} {r['name']}  PE={r['pe']} 息={r['div_yield']}%  ROE={r['roe']}%")
    html = gen_html(results, filtered, season_global, season_cn, score)
    out = "report.html"
    with open(out, "w", encoding="utf-8") as f: f.write(html)
    print(f"\n✅ 已生成：{out}")

if __name__ == "__main__":
    main()
