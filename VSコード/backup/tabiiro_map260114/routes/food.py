# routes/food.py

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, Food, Photo
from datetime import datetime
import os
import uuid

# 🔥 すべてのURLを /food/... に統一
food_bp = Blueprint("food", __name__, url_prefix="/food")


# ====================================================
# グルメ一覧（店舗ごとに集約）
# GET /food/gourmet/list
# ====================================================
@food_bp.route('/gourmet/list')
def gourmet_list():
    if not session.get('logged_in'):
        return redirect(url_for('auth.login'))

    user_id = session.get('user_id')
    foods = Food.query.filter_by(user_id=user_id).all()

    # 店舗名 → 記録一覧
    grouped = {}
    for f in foods:
        grouped.setdefault(f.shop_name, []).append(f)

    shop_summary = []
    for shop, items in grouped.items():
        avg = sum(i.evaluation for i in items) / len(items)

        # 🔥 その店舗の "全写真" の中から最新1枚をサムネイルにする
        all_photos = []
        for f in items:
            for ph in f.photos:
                all_photos.append((ph.photo_id, ph.filename))

        thumbnail = None
        if all_photos:
            latest = sorted(all_photos, key=lambda x: x[0], reverse=True)[0]
            thumbnail = latest[1]

        shop_summary.append({
            "shop_name": shop,
            "items": items,
            "avg": round(avg, 1),
            "count": len(items),
            "thumbnail": thumbnail
        })

    return render_template('gourmet_list.html', shop_summary=shop_summary)


# ====================================================
# 店舗ページ
# GET /food/shop/<shop_name>
# ====================================================
@food_bp.route('/shop/<shop_name>')
def shop_detail(shop_name):
    if not session.get('logged_in'):
        return redirect(url_for('auth.login'))

    user_id = session.get('user_id')
    items = Food.query.filter_by(user_id=user_id, shop_name=shop_name).all()

    if not items:
        flash("データが存在しません。", "error")
        return redirect(url_for('food.gourmet_list'))

    avg = round(sum(i.evaluation for i in items) / len(items), 1)

    # 🔥 最新写真をサムネイルにする
    all_photos = []
    for f in items:
        for ph in f.photos:
            all_photos.append((ph.photo_id, ph.filename))

    thumbnail = None
    if all_photos:
        latest = sorted(all_photos, key=lambda x: x[0], reverse=True)[0]
        thumbnail = latest[1]

    return render_template(
        'shop_detail.html',
        shop_name=shop_name,
        items=items,
        avg=avg,
        count=len(items),
        thumbnail=thumbnail
    )


# ====================================================
# グルメ記録登録ページ
# GET /food/gourmet/record
# ====================================================
@food_bp.route('/gourmet/record')
def gourmet_record():
    if not session.get('logged_in'):
        return redirect(url_for('auth.login'))
    return render_template('gourmet_record.html')


# ====================================================
# グルメ記録追加
# POST /food/gourmet/add
# ====================================================
@food_bp.route('/gourmet/add', methods=['POST'])
def add_gourmet():
    if not session.get('logged_in'):
        return redirect(url_for('auth.login'))

    user_id = session.get('user_id')

    shop_name = request.form.get('shop_name')
    food_name = request.form.get('food_name')
    visit_date = datetime.strptime(request.form.get('visit_date'), "%Y-%m-%d").date()
    evaluation = int(request.form.get('evaluation'))
    memo = request.form.get('memo')

    new_food = Food(
        user_id=user_id,
        shop_name=shop_name,
        food_name=food_name,
        visit_date=visit_date,
        evaluation=evaluation,
        memo=memo
    )

    db.session.add(new_food)
    db.session.flush()  # 新規 ID の取得

    upload_dir = os.path.join("static", "uploads")
    os.makedirs(upload_dir, exist_ok=True)

    # 🔥 写真衝突防止 → UUID 方式
    photos = request.files.getlist("photos[]")
    for p in photos:
        if not p.filename:
            continue

        filename = f"{user_id}_{uuid.uuid4().hex}_{p.filename}"
        p.save(os.path.join(upload_dir, filename))

        new_photo = Photo(
            user_id=user_id,
            food_id=new_food.food_id,
            filename=filename
        )
        db.session.add(new_photo)

    db.session.commit()

    flash("グルメ記録を登録しました！", "success")
    return redirect(url_for('food.gourmet_list'))


# ====================================================
# グルメ記録編集
# GET/POST /food/gourmet/<id>/edit
# ====================================================
@food_bp.route('/gourmet/<int:food_id>/edit', methods=['GET', 'POST'])
def gourmet_edit(food_id):
    if not session.get('logged_in'):
        return redirect(url_for('auth.login'))

    food = Food.query.get_or_404(food_id)

    if request.method == 'POST':
        food.shop_name = request.form.get('shop_name')
        food.food_name = request.form.get('food_name')
        food.evaluation = int(request.form.get('evaluation'))
        food.memo = request.form.get('memo')

        visit_date_str = request.form.get('visit_date')
        food.visit_date = datetime.strptime(visit_date_str, "%Y-%m-%d").date()

        upload_dir = os.path.join("static", "uploads")
        os.makedirs(upload_dir, exist_ok=True)

        # 🔥 UUID 方式に統一
        photos = request.files.getlist("photos[]")
        for p in photos:
            if not p.filename:
                continue

            filename = f"{food.user_id}_{uuid.uuid4().hex}_{p.filename}"
            p.save(os.path.join(upload_dir, filename))

            new_photo = Photo(
                user_id=food.user_id,
                food_id=food.food_id,
                filename=filename
            )
            db.session.add(new_photo)

        db.session.commit()

        flash("グルメ記録を更新しました！", "success")
        return redirect(url_for('food.gourmet_detail', food_id=food.food_id))

    return render_template('gourmet_edit.html', food=food)


# ====================================================
# グルメ記録詳細
# GET /food/gourmet/<id>
# ====================================================
@food_bp.route('/gourmet/<int:food_id>')
def gourmet_detail(food_id):
    if not session.get('logged_in'):
        return redirect(url_for('auth.login'))

    food = Food.query.get_or_404(food_id)

    related = Food.query.filter_by(
        user_id=food.user_id,
        shop_name=food.shop_name
    ).all()

    related_count = len(related)
    related_avg = sum(f.evaluation for f in related) / related_count

    return render_template(
        'gourmet_detail.html',
        food=food,
        related_count=related_count,
        related_avg=related_avg
    )


# ====================================================
# グルメ記録削除
# POST /food/gourmet/<id>/delete
# ====================================================
@food_bp.route('/gourmet/<int:food_id>/delete', methods=['POST'])
def gourmet_delete(food_id):
    if not session.get('logged_in'):
        return redirect(url_for('auth.login'))

    food = Food.query.get_or_404(food_id)

    db.session.delete(food)
    db.session.commit()

    flash("グルメ記録を削除しました。", "success")
    return redirect(url_for('food.gourmet_list'))


# ====================================================
# 写真削除
# POST /food/photo/<id>/delete
# ====================================================
@food_bp.route('/photo/<int:photo_id>/delete', methods=['POST'])
def delete_food_photo(photo_id):
    if not session.get('logged_in'):
        return redirect(url_for('auth.login'))

    photo = Photo.query.get_or_404(photo_id)
    user_id = session.get('user_id')

    if photo.user_id != user_id:
        flash("削除権限がありません。", "error")
        return redirect(url_for('food.gourmet_list'))

    filepath = os.path.join("static", "uploads", photo.filename)
    if os.path.exists(filepath):
        os.remove(filepath)

    food_id = photo.food_id

    db.session.delete(photo)
    db.session.commit()

    flash("写真を削除しました！", "success")
    return redirect(url_for('food.gourmet_edit', food_id=food_id))
