from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, User

# /user を prefix に統一
user_bp = Blueprint("user", __name__, url_prefix="/user")


# ====================================================
# ユーザー情報ページ
#   GET /user/data
# ====================================================
@user_bp.route('/data', methods=['GET'])
def user_data():
    if not session.get('logged_in'):
        return redirect(url_for('auth.login'))

    user = User.query.get(session.get('user_id'))
    return render_template('user_data.html', user=user)


# ====================================================
# ユーザー情報更新
#   POST /user/data
# ====================================================
@user_bp.route('/data', methods=['POST'])
def update_user_data():
    if not session.get('logged_in'):
        return redirect(url_for('auth.login'))

    user = User.query.get(session.get('user_id'))
    new_email = request.form.get('email')

    if not new_email:
        flash("メールアドレスを入力してください。", "error")
        return redirect(url_for('user.user_data'))

    # 他ユーザーと重複チェック
    existing = User.query.filter_by(email=new_email).first()
    if existing and existing.id != user.id:
        flash("このメールアドレスはすでに使用されています。", "error")
        return redirect(url_for('user.user_data'))

    user.email = new_email
    db.session.commit()

    flash("ユーザー情報を更新しました！", "success")
    return redirect(url_for('user.user_data'))


# ====================================================
# アカウント削除
#   POST /user/delete
# ====================================================
@user_bp.route('/delete', methods=['POST'])
def delete_account():
    if not session.get('logged_in'):
        return redirect(url_for('auth.login'))

    user = User.query.get(session.get('user_id'))

    db.session.delete(user)
    db.session.commit()

    session.clear()

    flash("アカウントを削除しました。", "success")
    return redirect(url_for('home'))

@user_bp.route('/change-password', methods=['GET', 'POST'])
def change_password():
    if not session.get('logged_in'):
        return redirect(url_for('auth.login'))

    user = User.query.get(session.get('user_id'))

    if request.method == "POST":
        current_pwd = request.form.get("current_pwd")
        new_pwd = request.form.get("new_pwd")
        confirm_pwd = request.form.get("confirm_pwd")

        # 現在のパスワード確認
        if not check_password_hash(user.password, current_pwd):
            flash("現在のパスワードが正しくありません。", "error")
            return redirect(url_for('user.change_password'))

        # 新パスワード一致確認
        if new_pwd != confirm_pwd:
            flash("新しいパスワードが一致しません。", "error")
            return redirect(url_for('user.change_password'))

        # 更新
        user.password = generate_password_hash(new_pwd)
        db.session.commit()

        flash("パスワードを変更しました！", "success")
        return redirect(url_for('user.user_data'))

    return render_template('change_password.html')
