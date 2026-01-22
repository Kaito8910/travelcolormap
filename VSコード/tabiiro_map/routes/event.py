# routes/event.py
from flask import Blueprint, render_template, request
from models import Event
from utils.json_loader import get_prefecture_list

event_bp = Blueprint("event", __name__, url_prefix="/event")


@event_bp.route("/search/results")
def event_search_results():
    prefecture = request.args.get("prefecture", "")
    month = request.args.get("month", "")
    period = request.args.get("period", "")
    keyword = request.args.get("keyword", "").strip()

    query = Event.query

    if prefecture:
        query = query.filter(Event.pref_name == prefecture)

    if month:
        query = query.filter(Event.month.contains(f"{month}月"))

    if period:
        query = query.filter(Event.month.contains(period))

    if keyword:
        query = query.filter(
            Event.title.contains(keyword) |
            Event.description.contains(keyword)
        )

    results = query.all()
    print("EVENT SEARCH RESULT COUNT:", len(results))

    return render_template(
        "event_search_results.html",
        results=results,
        prefectures=get_prefecture_list(),
        months=list(range(1, 13)),
        periods=["上旬", "中旬", "下旬"]
    )


@event_bp.route("/search")
def event_search():
    return render_template(
        "event_search.html",
        prefectures=get_prefecture_list(),
        months=list(range(1, 13)),
        periods=["上旬", "中旬", "下旬"]
    )
