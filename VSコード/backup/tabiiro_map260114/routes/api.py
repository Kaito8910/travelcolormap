# routes/api.py

from flask import Blueprint, jsonify, session
from models import Spot

# /api を prefix に設定
api_bp = Blueprint("api", __name__, url_prefix="/api")


# ====================================================
# 都道府県別の訪問回数取得
#   GET /api/pref-counts
# ====================================================
@api_bp.route('/pref-counts', methods=['GET'])
def api_pref_counts():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({})

    spots = Spot.query.filter_by(user_id=user_id).all()

    pref_counts = {}
    for spot in spots:
        pref = spot.prefecture.strip()
        pref_counts[pref] = pref_counts.get(pref, 0) + 1

    return jsonify(pref_counts)
