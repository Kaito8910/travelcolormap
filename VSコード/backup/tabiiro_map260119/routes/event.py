# routes/event.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from utils.json_loader import load_events_json, get_prefecture_list
import requests

# 🔥 すべてのURLが /event/... に統一
event_bp = Blueprint("event", __name__, url_prefix="/event")

CONNPASS_API_URL = "https://connpass.com/api/v2/events/"
API_TOKEN = "k0ojDAFr.NMjNt9vSGq9tjmx4JeKQQ6U97tkLSH7RRJNGgyCcUbo1U6Xi8lWIw7oc"


# -----------------------------------------------------------
# イベント検索結果
#   /event/search/results
# -----------------------------------------------------------
@event_bp.route('/search/results')
def event_search_results():
    EVENTS_JSON = load_events_json()

    prefecture = request.args.get("prefecture", "")
    month = request.args.get("month", "")
    period = request.args.get("period", "")
    keyword = request.args.get("keyword", "").strip()

    results = []

    for pref in EVENTS_JSON:
        pref_name = pref["pref_name_ja"]

        if prefecture and pref_name != prefecture:
            continue

        for ev in pref["events"]:
            ev_month_full = ev.get("month", "")

            # 月を抽出（例: "8月上旬" → 8）
            ev_month_num = ""
            for n in range(1, 13):
                if f"{n}月" in ev_month_full:
                    ev_month_num = str(n)
                    break

            if month and month != ev_month_num:
                continue

            if period and period not in ev_month_full:
                continue

            if keyword:
                if keyword not in ev.get("event_name", "") \
                   and keyword not in ev.get("description", ""):
                    continue

            results.append({
                "event_id": ev.get("event_id", ""),
                "event_name": ev.get("event_name", ""),
                "month": ev.get("month", ""),
                "city": ev.get("city", ""),
                "category": ev.get("category", ""),
                "description": ev.get("description", ""),
                "pref_name": pref_name,
                "event_url": ev.get("event_url", "")
            })

    return render_template(
        "event_search_results.html",
        results=results,
        prefectures=get_prefecture_list(),
        months=list(range(1, 13)),
        periods=["上旬", "中旬", "下旬"]
    )


# -----------------------------------------------------------
# イベント検索フォーム
#   /event/search
# -----------------------------------------------------------
@event_bp.route("/search")
def event_search():
    return render_template(
        "event_search.html",
        prefectures=get_prefecture_list(),
        months=list(range(1, 13)),
        periods=["上旬", "中旬", "下旬"]
    )
