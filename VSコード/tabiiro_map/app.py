from flask import (
    Flask,
    render_template,
    jsonify,
    session,
    redirect,
    url_for,
    request,
    flash,
)
import requests
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 本番では必ず安全なキーに変更すること


# ===============================================================
# ✨ データベース & マイグレーション設定
# ===============================================================
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///travel_records.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy()
db.init_app(app)
migrate = Migrate(app, db)


# ===============================================================
# 👤 ユーザーモデル
# ===============================================================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


# ===============================================================
# 🗾 都道府県訪問記録モデル（全ユーザー共通）
# ===============================================================
class TravelRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prefecture = db.Column(db.String(50), unique=True, nullable=False)
    visit_count = db.Column(db.Integer, nullable=False, default=0)


# ===============================================================
# 🏠 ホーム
# ===============================================================
@app.route('/')
def home():
    logged_in = session.get('logged_in', False)
    return render_template('home.html', logged_in=logged_in)


# ===============================================================
# 👤 ログイン
# ===============================================================
@app.route('/login', methods=['GET', 'POST'])
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

        flash('ログインに失敗しました。メールアドレスかパスワードが違います。', 'error')
        return redirect(url_for('login'))

    return render_template('login.html')


# ===============================================================
# ⭐ 新規登録
# ===============================================================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # 入力チェック
        if password != confirm_password:
            flash('パスワードが一致しません。', 'error')
            return redirect(url_for('register'))

        if not username or not email or not password:
            flash('すべての項目を入力してください。', 'error')
            return redirect(url_for('register'))

        # 重複チェック
        if User.query.filter_by(email=email).first():
            flash('このメールアドレスはすでに使われています。', 'error')
            return redirect(url_for('register'))

        if User.query.filter_by(username=username).first():
            flash('このユーザー名はすでに使われています。', 'error')
            return redirect(url_for('register'))

        # パスワードハッシュ化
        hashed_pass = generate_password_hash(password)

        new_user = User(username=username, email=email, password=hashed_pass)
        db.session.add(new_user)
        db.session.commit()

        flash('ユーザー登録が完了しました！ログインしてください。', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


# ===============================================================
# 👤 ログアウト
# ===============================================================
@app.route('/logout')
def logout():
    session.clear()
    return render_template('logout.html')


# ===============================================================
# ⭐ ユーザー情報表示
# ===============================================================
@app.route('/user-data', methods=['GET'])
def user_data():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    user = User.query.get(session.get('user_id'))

    if not user:
        flash("ユーザー情報が見つかりません。", "error")
        return redirect(url_for('home'))

    return render_template('user_data.html', user=user)


# ===============================================================
# ⭐ ユーザー情報更新（メール更新）
# ===============================================================
@app.route('/user-data', methods=['POST'])
def update_user_data():

    if not session.get('logged_in'):
        return redirect(url_for('login'))

    user = User.query.get(session.get('user_id'))

    if not user:
        flash("ユーザー情報が見つかりません。", "error")
        return redirect(url_for('home'))

    new_email = request.form.get('email')

    # 入力チェック
    if not new_email:
        flash("メールアドレスを入力してください。", "error")
        return redirect(url_for('user_data'))

    # メール重複チェック（自分以外）
    existing = User.query.filter_by(email=new_email).first()
    if existing and existing.id != user.id:
        flash("このメールアドレスはすでに使用されています。", "error")
        return redirect(url_for('user_data'))

    # 更新
    user.email = new_email
    db.session.commit()

    flash("ユーザー情報を更新しました！", "success")
    return redirect(url_for('user_data'))


# ===============================================================
# ⭐ アカウント削除
# ===============================================================
@app.route('/delete-account', methods=['POST'])
def delete_account():
    if not session.get('logged_in'):
        flash("ログインしてください。", "error")
        return redirect(url_for('login'))

    user = User.query.get(session.get('user_id'))

    if not user:
        flash("ユーザーが見つかりません。", "error")
        return redirect(url_for('user_data'))

    # アカウント削除
    db.session.delete(user)
    db.session.commit()

    session.clear()

    flash("アカウントを削除しました。ご利用ありがとうございました。", "success")
    return redirect(url_for('home'))


# ===============================================================
# ⭐ パスワード変更（ログイン中）
# ===============================================================
@app.route('/change-pwd', methods=['GET', 'POST'])
def change_pwd():

    if not session.get('logged_in'):
        return redirect(url_for('login'))

    user = User.query.get(session.get('user_id'))

    if request.method == 'POST':
        current_pwd = request.form.get('current_pwd')
        new_pwd = request.form.get('new_pwd')
        confirm_pwd = request.form.get('confirm_pwd')

        if not current_pwd or not new_pwd or not confirm_pwd:
            flash('すべての項目を入力してください。', 'error')
            return redirect(url_for('change_pwd'))

        if not check_password_hash(user.password, current_pwd):
            flash('現在のパスワードが違います。', 'error')
            return redirect(url_for('change_pwd'))

        if new_pwd != confirm_pwd:
            flash('新しいパスワードが一致しません。', 'error')
            return redirect(url_for('change_pwd'))

        user.password = generate_password_hash(new_pwd)
        db.session.commit()

        flash('パスワードを変更しました！', 'success')
        return redirect(url_for('user_data'))

    return render_template('change_pwd.html')


# ===============================================================
# ⭐ パスワード再設定（ログアウト時）
# ===============================================================
@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():

    if request.method == 'POST':
        email = request.form.get('email')

        if not email:
            flash("メールアドレスを入力してください。", "error")
            return redirect(url_for('forgot_password'))

        user = User.query.filter_by(email=email).first()

        if not user:
            flash("このメールアドレスは登録されていません。", "error")
            return redirect(url_for('forgot_password'))

        # 次の画面に渡す用
        session['reset_email'] = email

        return redirect(url_for('reset_password'))

    return render_template('forgot_password.html')


@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():

    reset_email = session.get('reset_email')
    if not reset_email:
        flash("メールアドレスが確認できません。もう一度やり直してください。", "error")
        return redirect(url_for('forgot_password'))

    user = User.query.filter_by(email=reset_email).first()

    if not user:
        flash("該当ユーザーが見つかりませんでした。", "error")
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        new_pwd = request.form.get('new_pwd')
        confirm_pwd = request.form.get('confirm_pwd')

        if not new_pwd or not confirm_pwd:
            flash("パスワードを入力してください。", "error")
            return redirect(url_for('reset_password'))

        if new_pwd != confirm_pwd:
            flash("パスワードが一致しません。", "error")
            return redirect(url_for('reset_password'))

        user.password = generate_password_hash(new_pwd)
        db.session.commit()

        session.pop('reset_email', None)

        flash("パスワードを更新しました。ログインしてください。", "success")
        return redirect(url_for('login'))

    return render_template('reset_password.html')


# ===============================================================
# その他のページ
# ===============================================================
@app.route('/travel-record')
def travel_record():
    return "<h1>旅行先記録ページ</h1>"


@app.route('/gourmet-record')
def gourmet_record():
    return "<h1>グルメ記録ページ</h1>"


@app.route('/stay-search')
def stay_search():
    return "<h1>宿泊検索ページ</h1>"


@app.route('/event-search')
def event_search():
    return render_template('event_search.html')


# ===============================================================
# API（都道府県訪問記録）
# ===============================================================
@app.route('/api/travel-records-db')
def travel_records_db_api():

    records = TravelRecord.query.all()
    data = {}

    for r in records:
        if r.visit_count == 0:
            status = "none"
        elif r.visit_count <= 2:
            status = "light"
        elif r.visit_count <= 5:
            status = "medium"
        else:
            status = "heavy"

        data[r.prefecture] = {
            "visit_count": r.visit_count,
            "status": status
        }

    return jsonify(data)


# ===============================================================
# 🎉 イベント検索API
# ===============================================================
@app.route('/event-search-results', methods=['POST'])
def event_search_results():

    area = request.form.get('area', '')
    category = request.form.get('category', '')
    date = request.form.get('date', '')  # 今回使っていないが将来のため残す

    keyword_list = [area, category]
    api_keyword = " ".join(filter(None, keyword_list))

    params = {
        'key': "7e7c8f15291d905e",
        'keyword': api_keyword,
        'format': 'json',
        'count': 5
    }

    events = []

    try:
        resp = requests.get("https://webservice.recruit.co.jp/ab-event/v1/", params=params, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            results = data.get('results', {}).get('event', [])
            for e in results:
                events.append({
                    'name': e.get('event_name', '不明なイベント'),
                    'period': f"{e.get('event_start_date', '')} ～ {e.get('event_end_date', '')}",
                    'location': e.get('event_place', ''),
                    'summary': (e.get('event_caption', '')[:100] + "...") if e.get('event_caption') else ''
                })
    except Exception as ex:
        print("イベント取得エラー:", ex)

    return render_template(
        'event_search_results.html',
        events=events,
        area=area,
        category=category,
        date=date
    )






# ===============================================================
# アプリ起動
# ===============================================================


# ==== 仮データ（本来はDBやAPIから取得） ====
SPOT_DATA = [
    {
        "name": "東京タワー",
        "address": "東京都港区芝公園4-2-8",
        "category": "観光地",
        "description": "東京の iconic なランドマーク。",
    },
    {
        "name": "浅草寺",
        "address": "東京都台東区浅草2-3-1",
        "category": "寺院",
        "description": "国内外から人気の観光スポット。",
    },
    {
        "name": "ユニバーサルスタジオジャパン",
        "address": "大阪府大阪市此花区桜島2丁目",
        "category": "テーマパーク",
        "description": "映画の世界が楽しめる人気スポット。",
    },
]


# ==== 検索フォーム ====
@app.route('/spot-search', methods=['GET'])
def spot_search():
    return render_template('spot_search.html')


# ==== 検索結果 ====
@app.route('/spot-search-results', methods=['POST'])
def spot_search_results():
    keyword = request.form.get('keyword', '').strip()

    # キーワードを含むものを検索
    results = []
    for s in SPOT_DATA:
        if keyword in s["name"] or keyword in s["address"] or keyword in s["category"]:
            results.append(s)

    return render_template(
        "spot_search_results.html",
        keyword=keyword,
        results=results
    )


if __name__ == "__main__":
    app.run(debug=True)







# ===============================================================
# アプリ起動
# ===============================================================
if __name__ == '__main__':
    app.run(debug=True)
