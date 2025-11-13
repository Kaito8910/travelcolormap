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
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 本番では安全なキーに変更！

# === APIキー設定 ===
JARAN_API_KEY = "7e7c8f15291d905e"
WEATHER_API_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
JARAN_URL = "https://webservice.recruit.co.jp/ab-event/v1/"
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"

# === データベース設定 ===
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///travel_records.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# ===============================================================
# 👤 ユーザーモデル（新規追加）
# ===============================================================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


# ===============================================================
# 🗾 都道府県ごとの訪問記録モデル
# ===============================================================
class TravelRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prefecture = db.Column(db.String(50), unique=True, nullable=False)
    visit_count = db.Column(db.Integer, nullable=False, default=0)


# --- 初回のみ実行してテーブルを作成 ---
# with app.app_context():
#     db.create_all()


# ===============================================================
# 🏠 ホーム画面（日本地図表示）
# ===============================================================
@app.route('/')
def home():
    logged_in = session.get('logged_in', False)
    return render_template('home.html', logged_in=logged_in)


# ===============================================================
# 👤 ログイン・ログアウト・アカウント管理
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
        else:
            flash('ログインに失敗しました。メールアドレスかパスワードが違います。', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')


# ⭐⭐⭐⭐⭐ ここを完全に書き換え！（DBに登録できるregister）
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

        # 既存チェック
        if User.query.filter_by(email=email).first():
            flash('このメールアドレスはすでに使われています。', 'error')
            return redirect(url_for('register'))

        if User.query.filter_by(username=username).first():
            flash('このユーザー名はすでに使われています。', 'error')
            return redirect(url_for('register'))

        # パスワードハッシュ化して保存
        hashed_pass = generate_password_hash(password)

        new_user = User(username=username, email=email, password=hashed_pass)
        db.session.add(new_user)
        db.session.commit()

        flash('ユーザー登録が完了しました！ログインしてください。', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    return render_template('logout.html')




# === ユーザー情報確認画面（GET表示） ===
@app.route('/user-data', methods=['GET'])
def user_data():
    return render_template('user_data.html')  # ← HTMLファイル名に合わせて変更


# === ユーザー情報更新処理（POST送信） ===
@app.route('/user-data', methods=['POST'])
def update_user_data():
    email = request.form.get('email')
    password = request.form.get('password')

    # 仮の処理（データベース接続なし）
    if not email or not password:
        flash('入力内容に不備があります。', 'error')
    else:
        flash('ユーザー情報を更新しました！', 'success')

    return redirect(url_for('user_data'))

# --- パスワード変更ページ ---
@app.route('/change-pwd', methods=['GET', 'POST'])
def change_pwd():
    if request.method == 'POST':
        current_pwd = request.form.get('current_pwd')
        new_pwd = request.form.get('new_pwd')
        confirm_pwd = request.form.get('confirm_pwd')

        if not current_pwd or not new_pwd or not confirm_pwd:
            flash('すべての項目を入力してください。', 'error')
        elif new_pwd != confirm_pwd:
            flash('新しいパスワードと確認用パスワードが一致しません。', 'error')
        elif current_pwd != 'password':  # 仮データ：現在のパスワード
            flash('現在のパスワードが正しくありません。', 'error')
        else:
            flash('パスワードを変更しました！', 'success')
            return redirect(url_for('user_data'))

    return render_template('change_pwd.html')


# ===============================================================
# 📖 各種ページ
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


@app.route('/event-search', methods=['GET'])
def event_search():
    return render_template('event_search.html')


@app.route('/spot-search')
def spot_search():
    return render_template('spot_search.html')


# ===============================================================
# 🗾 日本地図データ API（DB連携）
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
# 🎉 イベント検索機能 (じゃらんAPI)
# ===============================================================
@app.route('/event-search-results', methods=['POST'])
def event_search_results():
    area = request.form.get('area', '')
    category = request.form.get('category', '')
    date = request.form.get('date', '')

    keyword_list = [area, category]
    api_keyword = " ".join(filter(None, keyword_list))

    params = {
        'key': JARAN_API_KEY,
        'keyword': api_keyword,
        'format': 'json',
        'count': 5
    }

    events = []
    try:
        resp = requests.get(JARAN_URL, params=params, timeout=5)
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
        events = []

    return render_template(
        'event_search_results.html',
        events=events,
        area=area,
        category=category,
        date=date
    )


# ===============================================================
# 🧭 アプリ起動
# ===============================================================
if __name__ == '__main__':
    app.run(debug=True)
