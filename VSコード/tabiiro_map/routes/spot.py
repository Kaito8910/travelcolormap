# routes/spot.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import datetime
import os
import requests
from config import PREF_LATLON, PREF_LIST
from utils.weather_utils import convert_weather_icon
from sqlalchemy.exc import InvalidRequestError, OperationalError
from models import db, Spot, Photo, TravelRecord, Spots
from sqlalchemy import or_

# =============================================
# /spot をルートに統一
# =============================================
spot_bp = Blueprint("spot", __name__, url_prefix="/spot")


# ====================================================
# 観光地登録
#   GET  /spot/register
#   POST /spot/register
# ====================================================
@spot_bp.route('/register', methods=['GET', 'POST'])
def spot_register():
    if not session.get('logged_in'):
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        user_id = session.get('user_id')

        spot_name = request.form.get("spot_name")
        pref_full = request.form.get("prefecture")
        visit_date_str = request.form.get('visit_date')
        comment = request.form.get('comment')

        if not spot_name:
            flash("観光地名を入力してください。", "error")
            return redirect(url_for('spot.spot_register'))

        if not pref_full:
            flash("都道府県を選択してください。", "error")
            return redirect(url_for('spot.spot_register'))

        # 北海道以外は短縮
        pref_short = pref_full if pref_full == "北海道" else pref_full.replace("都","").replace("府","").replace("県","")

        visit_date = datetime.strptime(visit_date_str, "%Y-%m-%d").date()

        # ===== 天気API =====
        lat, lon = PREF_LATLON.get(pref_short, (None, None))
        weather = temp_max = temp_min = precipitation = None

        if lat and lon:
            url = (
                "https://archive-api.open-meteo.com/v1/archive"
                f"?latitude={lat}&longitude={lon}"
                f"&start_date={visit_date}&end_date={visit_date}"
                "&daily=weathercode,temperature_2m_max,temperature_2m_min,precipitation_sum"
                "&timezone=Asia/Tokyo"
            )
            try:
                res = requests.get(url).json()
                code = res["daily"]["weathercode"][0]
                weather = convert_weather_icon(code)
                temp_max = res["daily"]["temperature_2m_max"][0]
                temp_min = res["daily"]["temperature_2m_min"][0]
                precipitation = res["daily"]["precipitation_sum"][0]
            except Exception as e:
                print("天気取得失敗:", e)

        # ===== Spot 本体 =====
        new_spot = Spot(
            user_id=user_id,
            name=spot_name,
            prefecture=pref_short,
            visit_date=visit_date,
            comment=comment,
            weather=weather,
            temp_max=temp_max,
            temp_min=temp_min,
            precipitation=precipitation,
        )

        db.session.add(new_spot)
        db.session.flush()  # spot_id のため必須

        # ===== 写真複数保存 =====
        photos = request.files.getlist("photos[]")
        upload_dir = os.path.join("static", "uploads")
        os.makedirs(upload_dir, exist_ok=True)

        for p in photos:
            if not p or not p.filename:
                continue

            filename = f"{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{p.filename}"
            p.save(os.path.join(upload_dir, filename))

            new_photo = Photo(
                user_id=user_id,
                spot_id=new_spot.spot_id,
                filename=filename
            )
            db.session.add(new_photo)

        db.session.commit()

        flash("観光地を登録しました！（天気データ・写真も保存）", "success")
        return redirect(url_for('spot.spot_list'))

    return render_template("spot_register.html", prefectures=PREF_LIST)


# ====================================================
# 観光地一覧
#   GET /spot/list
# ====================================================
@spot_bp.route('/list', methods=['GET'])
def spot_list():
    if not session.get('logged_in'):
        return redirect(url_for('auth.login'))

    user_id = session.get('user_id')
    selected_pref = request.args.get('prefecture', '')

    if selected_pref:
        pref_short = selected_pref if selected_pref == "北海道" else selected_pref.replace("都","").replace("府","").replace("県","")
        spots = Spot.query.filter_by(
            user_id=user_id, prefecture=pref_short
        ).order_by(Spot.prefecture.asc(), Spot.name.asc()).all()
    else:
        spots = Spot.query.filter_by(user_id=user_id).order_by(
            Spot.prefecture.asc(), Spot.name.asc()
        ).all()

    return render_template(
        'spot_list.html',
        spots=spots,
        prefectures=PREF_LIST,
        selected_pref=selected_pref
    )


# ====================================================
# 観光地詳細
#   GET /spot/detail/<id>
# ====================================================
@spot_bp.route('/detail/<int:spot_id>')
def spot_detail(spot_id):
    if not session.get('logged_in'):
        return redirect(url_for('auth.login'))

    spot = Spot.query.get_or_404(spot_id)
    return render_template('spot_detail.html', spot=spot)


# ====================================================
# 観光地編集
#   GET, POST /spot/edit/<id>
# ====================================================
@spot_bp.route('/edit/<int:spot_id>', methods=['GET', 'POST'])
def spot_edit(spot_id):
    if not session.get('logged_in'):
        return redirect(url_for('auth.login'))

    spot = Spot.query.get_or_404(spot_id)

    if request.method == 'POST':
        # ===== 更新前の値を保持（差分判定用）=====
        old_prefecture = spot.prefecture
        old_visit_date = spot.visit_date

        # ===== フォーム反映 =====
        spot.name = request.form.get('spot_name')

        pref_full = request.form.get('prefecture')
        pref_short = pref_full if pref_full == "北海道" else pref_full.replace("都", "").replace("府", "").replace("県", "")
        spot.prefecture = pref_short

        visit_date_str = request.form.get('visit_date')
        spot.visit_date = datetime.strptime(visit_date_str, "%Y-%m-%d").date()

        spot.comment = request.form.get('comment')

        # ===== 天気更新判定：日付 or 都道府県が変わったときだけ =====
        needs_weather_update = (old_prefecture != spot.prefecture) or (old_visit_date != spot.visit_date)

        if needs_weather_update:
            lat, lon = PREF_LATLON.get(spot.prefecture, (None, None))

            if lat and lon:
                url = (
                    "https://archive-api.open-meteo.com/v1/archive"
                    f"?latitude={lat}&longitude={lon}"
                    f"&start_date={spot.visit_date}&end_date={spot.visit_date}"
                    "&daily=weathercode,temperature_2m_max,temperature_2m_min,precipitation_sum"
                    "&timezone=Asia/Tokyo"
                )
                try:
                    res = requests.get(url, timeout=5).json()

                    # daily が無い/空のときは上書きしない
                    daily = res.get("daily")
                    if daily and daily.get("weathercode"):
                        code = daily["weathercode"][0]
                        spot.weather = convert_weather_icon(code)
                        spot.temp_max = daily["temperature_2m_max"][0]
                        spot.temp_min = daily["temperature_2m_min"][0]
                        spot.precipitation = daily["precipitation_sum"][0]
                    else:
                        print("天気データなし:", res)

                except Exception as e:
                    print("天気取得失敗:", e)
            else:
                print("lat/lon が見つからない prefecture:", spot.prefecture)

        # ===== 写真追加（既存のまま）=====
        photos = request.files.getlist("photos[]")
        upload_dir = os.path.join("static", "uploads")
        os.makedirs(upload_dir, exist_ok=True)

        for p in photos:
            if not p.filename:
                continue

            filename = f"{spot.user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{p.filename}"
            p.save(os.path.join(upload_dir, filename))

            new_photo = Photo(
                user_id=spot.user_id,
                spot_id=spot.spot_id,
                filename=filename
            )
            db.session.add(new_photo)

        db.session.commit()

        flash("観光地情報を更新しました。", "success")
        return redirect(url_for('spot.spot_detail', spot_id=spot.spot_id))

    return render_template('spot_edit.html', spot=spot, prefectures=PREF_LIST)

# ====================================================
# 写真削除
#   POST /spot/photo/delete/<id>
# ====================================================
@spot_bp.route('/photo/delete/<int:photo_id>', methods=['POST'])
def delete_spot_photo(photo_id):
    if not session.get('logged_in'):
        return "Unauthorized", 401

    photo = Photo.query.get_or_404(photo_id)

    filepath = os.path.join("static", "uploads", photo.filename)
    if os.path.exists(filepath):
        os.remove(filepath)

    db.session.delete(photo)
    db.session.commit()

    return "OK", 200

# ============================================
# 📍 観光地検索フォーム
# ============================================
@spot_bp.route("/search", methods=["GET"])
def spot_search():
    selected_pref = request.args.get("prefecture", "").strip()
    prefectures = [
        r[0] for r in db.session.query(Spots.pref_name_ja)
        .distinct()
        .order_by(Spots.pref_code)
        .all()
        if r[0]
    ]
    return render_template("spot_search.html", prefectures=prefectures, selected_pref=selected_pref)


# ============================================
# 📍 観光地検索結果
# ============================================
@spot_bp.route("/search/result", methods=["GET"])
def spot_search_results():
    prefecture = request.args.get("prefecture", "").strip()
    keyword = request.args.get("keyword", "").strip()

    query = Spots.query

    if prefecture:
        query = query.filter(Spots.pref_name_ja == prefecture)

    if keyword:
        query = query.filter(
            or_(
                Spots.name.contains(keyword),
                Spots.description.contains(keyword),
            )
        )

    results = query.all()

    # プルダウン用：都道府県一覧（DBから）
    prefectures = [
        r[0] for r in db.session.query(Spots.pref_name_ja)
        .distinct()
        .order_by(Spots.pref_code)
        .all()
        if r[0]
    ]

    return render_template(
        "spot_search_results.html",
        results=results,
        prefectures=prefectures,
        selected_pref=prefecture,
        keyword=keyword
    )

# ====================================================
# 都道府県クリック時の分岐
#   GET /spot/pref/<pref_name>
#   ある: /spot/list?prefecture=〇〇
#   ない: /spot/search?prefecture=〇〇
# ====================================================
@spot_bp.route("/pref/<string:pref_name>", methods=["GET"])
def pref_click(pref_name):
    pref_full = pref_name.strip()
    if not session.get("logged_in"):
        return redirect(url_for("spot.spot_search_results", prefecture=pref_full, keyword=""))

    user_id = session.get("user_id")

    # Spotは短縮で保存されてるので短縮に合わせる
    pref_short = pref_full if pref_full == "北海道" else pref_full.replace("都", "").replace("府", "").replace("県", "")

    try:
        exists = Spot.query.filter_by(user_id=user_id, prefecture=pref_short).first() is not None
    except (InvalidRequestError, OperationalError, AttributeError):
        exists = (
            TravelRecord.query.filter_by(user_id=user_id, prefecture=pref_short).first()
            is not None
        )

    if exists:
        return redirect(url_for("spot.spot_list", prefecture=pref_full))
    else:
        # ★検索結果画面へ直行（keywordは空でOK）
        return redirect(url_for("spot.spot_search_results", prefecture=pref_full, keyword=""))

