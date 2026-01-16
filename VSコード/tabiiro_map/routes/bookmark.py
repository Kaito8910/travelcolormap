# routes/bookmark.py

from flask import Blueprint, render_template, request, url_for, redirect, flash, jsonify, session
from models import db, Bookmark

# 🔥 すべての URL が /bookmark/... に統一される
bookmark_bp = Blueprint("bookmark", __name__, url_prefix="/bookmark")


# -----------------------------
# ブックマーク一覧
# -----------------------------
@bookmark_bp.route('/list')
def bookmark_list():
    if not session.get('logged_in'):
        return redirect(url_for('auth.login'))

    user_id = session.get('user_id')
    filter_type = request.args.get('filter', 'all')

    query = Bookmark.query.filter_by(user_id=user_id)
    if filter_type != 'all':
        query = query.filter_by(target_type=filter_type)

    bookmarks = query.all()

    # spot の場合は内部リンクを自動生成
    for bm in bookmarks:
        if not bm.detail_url and bm.target_type == "spot":
            bm.detail_url = url_for("spot.spot_detail", spot_id=bm.target_id)

    return render_template('bookmark_list.html', bookmarks=bookmarks, filter=filter_type)


# -----------------------------
# ブックマーク追加（検索画面用）
# -----------------------------
@bookmark_bp.route('/add', methods=['POST'])
def add_bookmark():
    if not session.get('logged_in'):
        return jsonify({"ok": False, "msg": "LOGIN_REQUIRED"})

    user_id = session.get('user_id')
    target_type = request.form.get("type")
    target_id = request.form.get("id")
    title = request.form.get("title")
    thumb = request.form.get("thumb", "")
    detail_url = request.form.get("url", "")

    # すでに存在する場合は何もしない
    existing = Bookmark.query.filter_by(
        user_id=user_id, target_type=target_type, target_id=target_id
    ).first()

    if existing:
        return jsonify({"ok": True, "msg": "ALREADY_EXISTS"})

    new_bm = Bookmark(
        user_id=user_id,
        target_type=target_type,
        target_id=target_id,
        title=title,
        thumb=thumb,
        detail_url=detail_url
    )

    db.session.add(new_bm)
    db.session.commit()

    return jsonify({"ok": True})


# -----------------------------
# ブックマーク削除（検索画面用）
# -----------------------------
@bookmark_bp.route('/remove', methods=['POST'])
def remove_bookmark():
    if not session.get('logged_in'):
        return jsonify({"ok": False, "msg": "LOGIN_REQUIRED"})

    user_id = session.get('user_id')
    target_type = request.form.get("type")
    target_id = request.form.get("id")

    bm = Bookmark.query.filter_by(
        user_id=user_id, target_type=target_type, target_id=target_id
    ).first()

    if not bm:
        return jsonify({"ok": False, "msg": "NOT_FOUND"})

    db.session.delete(bm)
    db.session.commit()

    return jsonify({"ok": True})


# -----------------------------
# ブックマーク削除（一覧ページ用）
# -----------------------------
@bookmark_bp.route('/delete', methods=['POST'])
def bookmark_delete():
    if not session.get('logged_in'):
        flash("ログインしてください", "error")
        return redirect(url_for('auth.login'))

    user_id = session.get('user_id')
    target_type = request.form.get("type")
    target_id = request.form.get("id")

    bm = Bookmark.query.filter_by(
        user_id=user_id, target_type=target_type, target_id=target_id
    ).first()

    if not bm:
        flash("ブックマークが見つかりません", "error")
        return redirect(url_for('bookmark.bookmark_list'))

    db.session.delete(bm)
    db.session.commit()

    flash("ブックマークを削除しました", "success")
    return redirect(url_for('bookmark.bookmark_list'))
