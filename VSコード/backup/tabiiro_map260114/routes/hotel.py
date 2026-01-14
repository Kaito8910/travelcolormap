# routes/hotel.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.hotel_utils import search_hotels, extract_hotel_info
from models import db, Bookmark

# 🔥 /hotel を prefix に統一
hotel_bp = Blueprint("hotel", __name__, url_prefix="/hotel")


# ====================================================
# ホテル検索ページ
# GET /hotel/search
# POST /hotel/search
# ====================================================
@hotel_bp.route("/search", methods=["GET", "POST"])
def hotel_search():
    if request.method == "POST":
        kw = request.form.get("keyword", "").strip()

        if not kw:
            return render_template("hotel_search.html", error="キーワードを入力してください")

        # /hotel/results/<keyword> に遷移
        return redirect(url_for("hotel.hotel_results", keyword=kw))

    return render_template("hotel_search.html")


# ====================================================
# ホテル検索結果  
# GET /hotel/results/<keyword>
# ====================================================
@hotel_bp.route("/results/<keyword>")
def hotel_results(keyword):
    user_id = session.get("user_id")

    # API から情報取得
    raw_hotels = search_hotels(keyword)
    hotels = extract_hotel_info(raw_hotels)

    # ユーザーが既にブックマークしているホテルID一覧
    bookmarked_ids = {
        str(bm.target_id)
        for bm in Bookmark.query.filter_by(user_id=user_id, target_type="hotel").all()
    }

    # 各ホテルに「ブックマーク済み」フラグを付与
    for h in hotels:
        hotel_id = str(h.get("hotelNo"))
        h["is_bookmarked"] = hotel_id in bookmarked_ids

    return render_template("hotel_results.html", hotels=hotels, keyword=keyword)
