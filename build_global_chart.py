"""chart_component.py の CSS/HTML/JS を英語UIに翻訳する。

ロジックは一切変えず、ユーザーに見える文字列だけを置換する方式を取る
（コードを書き直すより、テスト済みの挙動をそのまま保てるため安全）。
置換は最長一致から行い、部分文字列の衝突（例: '暴落30%' ボタンと
裸の '暴落'）を避ける。各置換で出現回数を検査し、想定外の場所を
壊していないかを確認する。
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import chart_component as cc  # noqa: E402


def sub(s, old, new, n=1):
    c = s.count(old)
    if c != n:
        raise SystemExit(f"置換対象が{c}件（期待{n}）: {old[:60]!r}")
    return s.replace(old, new)


# 暴落名（順序を保つ。西暦を含むものはハイフンをenダッシュに）
CRASH_NAMES = [
    ("1957年不況", "1957 Recession"),
    ("ケネディ・スライド", "Kennedy Slide"),
    ("1966年調整", "1966 Correction"),
    ("1969-70年調整", "1969–70 Correction"),
    ("オイルショック", "Oil Shock"),
    ("1981-82年不況", "1981–82 Recession"),
    ("ブラックマンデー", "Black Monday"),
    ("湾岸危機", "Gulf War Crisis"),
    ("LTCM危機", "LTCM Crisis"),
    ("ITバブル崩壊", "Dot-com Crash"),
    ("リーマンショック", "Global Financial Crisis"),
    ("2018年末調整", "Late-2018 Correction"),
    ("コロナショック", "COVID Crash"),
    ("2022年調整", "2022 Correction"),
    ("2025年春の調整", "Spring 2025 Correction"),
]


def translate_chart(css, html, js):
    # ---- HTML: ボタン・ラベル ----
    html = sub(html, "リセット", "Reset")
    html = sub(html, "チャネル</button>", "Channel</button>")
    html = sub(html, "暴落30%", "Crash 30%")
    html = sub(html, "調整20%", "Correction 20%")
    html = sub(html, '>高度</button>', '>Altitude</button>')
    html = sub(html, ">期間<", ">Range<")
    html = sub(html, ">月足<", ">Monthly<")

    # ---- JS: 固定文言（長い/具体的なものから） ----
    js = sub(js, "チャネル適用外（99%が上限の外側）",
             "Outside channel (99% above ceiling)")
    js = sub(js, "チャネル内の位置（高度）", "Position in channel (Altitude)")
    js = sub(js, "表示できる期間がありません", "No data in this range")
    js = sub(js, "ホイールで拡大縮小 ／ ドラッグで移動 ／ ダブルクリックで全期間",
             "Scroll to zoom · Drag to pan · Double-click to reset")
    js = sub(js, "ピンチで拡大縮小 ／ 横になぞって移動 ／ ダブルタップで全期間",
             "Pinch to zoom · Swipe to pan · Double-tap to reset")
    js = sub(js, "['全期間 1871-',1871]", "['All 1871-',1871]")
    js = sub(js, "'1932- 有効域'", "'1932- valid'")

    # ---- JS: 暴落局面（裸の語を置換。ボタン文言はHTML側で既に消費済み） ----
    for jp, en in CRASH_NAMES:
        js = sub(js, f"n:'{jp}'", f"n:'{en}'")
    js = sub(js, "'局面</span>'", "' event</span>'")
    js = sub(js, "?'暴落':'調整'", "?'Crash':'Correction'")

    # ---- JS: 粒度（月足/週足/日足）とその単位 ----
    js = sub(js, "u:'ヶ月',p:'月足'", "u:' mo',p:'Monthly'")
    js = sub(js, "u:'週',p:'週足'", "u:' wk',p:'Weekly'")
    js = sub(js, "u:'日',p:'日足'", "u:' d',p:'Daily'")

    # ---- JS: 区切り文字（全角スペース→半角2つ） ----
    js = sub(js, "+'　'+VIS.length", "+'  '+VIS.length")

    # ---- JS: 週足ツールチップ見出し「〜の週」の語順を英語化 ----
    js = sub(js,
             "S.ym[b]+' 〜 '+S.ye[b].slice(5)+' の週'",
             "'Week of '+S.ym[b]+'–'+S.ye[b].slice(5)")

    # ---- JS: ツールチップの各ラベル ----
    js = sub(js, 'class="m">高<', 'class="m">High<')
    js = sub(js, 'class="m">安<', 'class="m">Low<')
    js = sub(js, 'class="m">月中平均<', 'class="m">Mid-month avg<')
    js = sub(js, 'class="m">終値<', 'class="m">Close<')
    js = sub(js, 'class="m">高度<', 'class="m">Altitude<')
    js = sub(js, 'class="m">上限100%<', 'class="m">Ceiling 100%<')
    js = sub(js, 'class="m">中央50%<', 'class="m">Mid 50%<')
    js = sub(js, 'class="m">下限0%<', 'class="m">Floor 0%<')

    # ---- JS: 右端ラベル「高度 xx.x%」の残り（裸の「高度 」） ----
    js = sub(js, "'高度 '+av.toFixed", "'Altitude '+av.toFixed")

    return css, html, js


def build_chart_en(csv_path=None, weekly_path=None, start=1932.4):
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = csv_path or os.path.join(base, "spx_long_1871.csv")
    weekly_path = weekly_path or os.path.join(base, "spx_weekly_1927.csv")
    css, html, js, n_mo, n_wk, n_dy = cc.build_chart(
        csv_path=csv_path, weekly_path=weekly_path, start=start)
    css, html, js = translate_chart(css, html, js)
    return css, html, js, n_mo, n_wk, n_dy


if __name__ == "__main__":
    css, html, js, n_mo, n_wk, n_dy = build_chart_en()
    print(f"翻訳完了: 月足{n_mo:,} / 週足{n_wk:,} / 日足{n_dy:,}")
    # 未翻訳の日本語が残っていないか（コード中のコメントは除外できないため、
    # ここではユーザーに見える文字列だけを再現したテスト用HTMLで別途確認する）
    import re
    remain = set(re.findall(r"[぀-ヿ一-鿿]", html))
    print("HTML内の残存CJK文字:", remain or "なし")
