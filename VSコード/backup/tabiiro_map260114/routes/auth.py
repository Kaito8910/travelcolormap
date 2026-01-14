from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

auth_bp = Blueprint("auth", __name__)


# ----------------- LOGIN -----------------
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['logged_in'] = True
            session['username'] = user.username
            session['user_id'] = user.id
            return redirect(url_for('home'))

        flash('ログインに失敗しました。', 'error')
        return redirect(url_for('auth.login'))

    return render_template('login.html')


# ----------------- REGISTER -----------------
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('パスワードが一致しません。', 'error')
            return redirect(url_for('auth.register'))

        if not username or not email or not password:
            flash('すべての項目を入力してください。', 'error')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(email=email).first():
            flash('このメールアドレスは使用されています。', 'error')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(username=username).first():
            flash('このユーザー名は使用されています。', 'error')
            return redirect(url_for('auth.register'))

        hashed = generate_password_hash(password)

        new_user = User(
            username=username,
            email=email,
            password=hashed
        )

        db.session.add(new_user)
        db.session.commit()

        flash('登録が完了しました！ログインしてください。', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


# ----------------- LOGOUT -----------------
@auth_bp.route('/logout')
def logout():
    session.clear()
    return render_template('logout.html')


# ----------------- FORGOT PASSWORD -----------------
@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()

        if not user:
            flash("メールアドレスが登録されていません。", "error")
            return redirect(url_for('auth.forgot_password'))

        session['reset_email'] = email
        return redirect(url_for('auth.reset_password'))

    return render_template('forgot_password.html')


@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    email = session.get('reset_email')
    if not email:
        flash("メールアドレス確認エラー", "error")
        return redirect(url_for('auth.forgot_password'))

    user = User.query.filter_by(email=email).first()

    if request.method == 'POST':
        new_pwd = request.form.get('new_pwd')
        confirm_pwd = request.form.get('confirm_pwd')

        if new_pwd != confirm_pwd:
            flash("パスワードが一致しません。", "error")
            return redirect(url_for('auth.reset_password'))

        user.password = generate_password_hash(new_pwd)
        db.session.commit()

        session.pop('reset_email', None)

        flash("パスワードを更新しました。", "success")
        return redirect(url_for('auth.login'))

    return render_template('reset_password.html')
