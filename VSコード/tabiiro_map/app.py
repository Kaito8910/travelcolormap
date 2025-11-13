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
        username = request.form.get('username')
        password = request.form.get('password')

        if username == 'user' and password == 'pass':
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('home'))
        else:
            flash('ログインに失敗しました。ユーザー名かパスワードが違います。', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('パスワードが一致しません。', 'error')
            return redirect(url_for('register'))

        if not username or not email or not password:
            flash('すべての項目を入力してください。', 'error')
            return redirect(url_for('register'))

        session['logged_in'] = True
        session['username'] = username
        flash('ユーザー登録が完了しました。', 'success')
        return redirect(url_for('home'))

    return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    return render_template('logout.html')


@app.route('/user-data')
def user_data():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    username = session.get('username', 'ゲスト')
    return f"<h1>{username} さんのアカウント情報ページ</h1>"


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
        # 行った回数に応じて自動でステータスを設定
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
