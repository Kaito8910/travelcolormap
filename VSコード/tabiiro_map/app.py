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
from spot_pref_map import SPOT_TO_PREF
from datetime import datetime
#import pandas as pd

app = Flask(__name__)
app.secret_key = 'your_secret_key'

API_KEY = "1002136947918553343"

# ===============================================================
# ✨ データベース & マイグレーション設定
# ===============================================================
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///travel_records.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy()
db.init_app(app)
migrate = Migrate(app, db)

# ===============================================================
# 🌟 DB モデル
# ===============================================================

# ---------------------------------------------------------------
# アカウント管理テーブル（USER）
# ---------------------------------------------------------------
class User(db.Model):
    __tablename__ = "USER"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False
    )

# ---------------------------------------------------------------
# 観光地管理テーブル（SPOT）
# ---------------------------------------------------------------
class Spot(db.Model):
    __tablename__ = "SPOT"

    spot_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("USER.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    prefecture = db.Column(db.String(20), nullable=False)
    visit_date = db.Column(db.Date, nullable=False)
    photo = db.Column(db.String(255))
    comment = db.Column(db.Text)
    weather = db.Column(db.String(50))   
    temp_max = db.Column(db.Float)        
    temp_min = db.Column(db.Float)         
    precipitation = db.Column(db.Float)     
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False
    )

# ---------------------------------------------------------------
# グルメ記録テーブル（FOOD）
# ---------------------------------------------------------------
class Food(db.Model):
    __tablename__ = "FOOD"

    food_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("USER.id"), nullable=False)
    shop_name = db.Column(db.String(100), nullable=False)
    food_name = db.Column(db.String(100))
    visit_date = db.Column(db.Date, nullable=False)
    evaluation = db.Column(db.Integer)
    memo = db.Column(db.Text)
    stay_id = db.Column(db.Integer, db.ForeignKey("STAY.stay_id"))
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False
    )

# ---------------------------------------------------------------
# 宿泊記録テーブル（STAY）
# ---------------------------------------------------------------
class Stay(db.Model):
    __tablename__ = "STAY"

    stay_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("USER.id"), nullable=False)
    hotel_name = db.Column(db.String(100), nullable=False)
    checkin_date = db.Column(db.Date, nullable=False)
    checkout_date = db.Column(db.Date, nullable=False)
    price = db.Column(db.Integer)
    memo = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False
    )

# ---------------------------------------------------------------
# ブックマーク管理テーブル（BOOKMARK）
# ---------------------------------------------------------------
class Bookmark(db.Model):
    __tablename__ = "BOOKMARK"

    bookmark_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("USER.id"), nullable=False)
    target_type = db.Column(db.String(30), nullable=False)
    target_id = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(100))
    thumb = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

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

        flash('ログインに失敗しました。', 'error')
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

        if password != confirm_password:
            flash('パスワードが一致しません。', 'error')
            return redirect(url_for('register'))

        if not username or not email or not password:
            flash('すべての項目を入力してください。', 'error')
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash('このメールアドレスは使用されています。', 'error')
            return redirect(url_for('register'))

        if User.query.filter_by(username=username).first():
            flash('このユーザー名は使用されています。', 'error')
            return redirect(url_for('register'))

        hashed = generate_password_hash(password)

        new_user = User(
            username=username,
            email=email,
            password=hashed
        )

        db.session.add(new_user)
        db.session.commit()

        flash('登録が完了しました！ログインしてください。', 'success')
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
    return render_template('user_data.html', user=user)

# ===============================================================
# ⭐ ユーザー情報更新
# ===============================================================
@app.route('/user-data', methods=['POST'])
def update_user_data():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    user = User.query.get(session.get('user_id'))
    new_email = request.form.get('email')

    if not new_email:
        flash("メールアドレスを入力してください。", "error")
        return redirect(url_for('user_data'))

    existing = User.query.filter_by(email=new_email).first()
    if existing and existing.id != user.id:
        flash("このメールアドレスはすでに使用されています。", "error")
        return redirect(url_for('user_data'))

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
        return redirect(url_for('login'))

    user = User.query.get(session.get('user_id'))

    db.session.delete(user)
    db.session.commit()

    session.clear()

    flash("アカウントを削除しました。", "success")
    return redirect(url_for('home'))

# ===============================================================
# ⭐ パスワード変更
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

        if not check_password_hash(user.password, current_pwd):
            flash('現在のパスワードが違います。', 'error')
            return redirect(url_for('change_pwd'))

        if new_pwd != confirm_pwd:
            flash('パスワードが一致しません。', 'error')
            return redirect(url_for('change_pwd'))

        user.password = generate_password_hash(new_pwd)
        db.session.commit()

        flash('パスワードを変更しました！', 'success')
        return redirect(url_for('user_data'))

    return render_template('change_pwd.html')

# ===============================================================
# ⭐ パスワード再設定
# ===============================================================
@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()

        if not user:
            flash("メールアドレスが登録されていません。", "error")
            return redirect(url_for('forgot_password'))

        session['reset_email'] = email
        return redirect(url_for('reset_password'))

    return render_template('forgot_password.html')

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    email = session.get('reset_email')
    if not email:
        flash("メールアドレス確認エラー", "error")
        return redirect(url_for('forgot_password'))

    user = User.query.filter_by(email=email).first()

    if request.method == 'POST':
        new_pwd = request.form.get('new_pwd')
        confirm_pwd = request.form.get('confirm_pwd')

        if new_pwd != confirm_pwd:
            flash("パスワードが一致しません。", "error")
            return redirect(url_for('reset_password'))

        user.password = generate_password_hash(new_pwd)
        db.session.commit()

        session.pop('reset_email', None)

        flash("パスワードを更新しました。", "success")
        return redirect(url_for('login'))

    return render_template('reset_password.html')

# ===============================================================
# スポット登録
# ===============================================================
@app.route('/spot-register', methods=['GET', 'POST'])
def spot_register():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        user_id = session.get('user_id')
        prefecture = request.form.get("prefecture")
        visit_date = datetime.strptime(request.form.get('visit_date'), "%Y-%m-%d").date()
        comment = request.form.get('comment')
        name = request.form.get('name')

        # 写真処理
        photo_file = request.files.get('photo')
        filename = None
        if photo_file and photo_file.filename:
            upload_dir = os.path.join("static", "uploads")
            os.makedirs(upload_dir, exist_ok=True)
            filename = f"{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{photo_file.filename}"
            photo_file.save(os.path.join(upload_dir, filename))

        # ▼▼ 天気取得 ▼▼
        lat, lon = PREF_LATLON.get(prefecture, (None, None))
        weather = None
        temp_max = None
        temp_min = None
        precipitation = None

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
            except:
                print("天気取得失敗")

        # ▼▼ DB 保存 ▼▼
        new_spot = Spot(
            user_id=user_id,
            name=name,
            prefecture=prefecture,
            visit_date=visit_date,
            photo=filename,
            comment=comment,
            weather=weather,
            temp_max=temp_max,
            temp_min=temp_min,
            precipitation=precipitation,
        )

        db.session.add(new_spot)
        db.session.commit()

        flash("登録しました！（天気データも保存しました）", "success")
        return redirect(url_for('spot_register'))

    return render_template("spot_register.html")

# ===============================================================
#グルメ記録登録
# ===============================================================

@app.route('/gourmet-record')
def gourmet_record():
    return render_template('gourmet_record.html')

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
# API — 都道府県カウント
# ===============================================================
@app.route('/api/pref_counts')
def api_pref_counts():
    spots = Spot.query.all()
    pref_counts = {}

    for spot in spots:
        for keyword, pref in SPOT_TO_PREF.items():
            if keyword in spot.name:
                pref_counts[pref] = pref_counts.get(pref, 0) + 1

    return jsonify(pref_counts)

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

EVENT_DATA = [
    {
        "name": "祭り",
        "address": "東京都港区芝公園4-2-8",
        "category": "観光地",
        "description": "東京の iconic なランドマーク。",
    },
    {
        "name": "お花見",
        "address": "東京都台東区浅草2-3-1",
        "category": "寺院",
        "description": "国内外から人気の観光スポット。",
    },
    {
        "name": "ショー",
        "address": "大阪府大阪市此花区桜島2丁目",
        "category": "テーマパーク",
        "description": "映画の世界が楽しめる人気スポット。",
    },
]

# ===============================================================
# スポット検索
# ===============================================================

# ==== 検索フォーム ====
@app.route('/spot-search', methods=['GET'])
def spot_search():
    PREF_LIST = [
        "北海道","青森県","岩手県","宮城県","秋田県","山形県","福島県",
        "茨城県","栃木県","群馬県","埼玉県","千葉県","東京都","神奈川県",
        "新潟県","富山県","石川県","福井県","山梨県","長野県","岐阜県",
        "静岡県","愛知県","三重県","滋賀県","京都府","大阪府","兵庫県",
        "奈良県","和歌山県","鳥取県","島根県","岡山県","広島県","山口県",
        "徳島県","香川県","愛媛県","高知県","福岡県","佐賀県","長崎県",
        "熊本県","大分県","宮崎県","鹿児島県","沖縄県"
    ]

    return render_template(
        'spot_search.html',
        prefectures=PREF_LIST
    )

# ==== 検索結果 ====
@app.route('/spot-search-results', methods=['GET'])
def spot_search_results():
    prefecture = request.args.get('prefecture', '')
    keyword = request.args.get('keyword', '')

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

# ===============================
# 宿泊検索（検索フォーム）
# ===============================

RAKUTEN_API_KEY = "1002136947918553343"

# ▼ 楽天公式の正しい都道府県コード（最低限版）
PREFECTURES = [
    {"name": "北海道", "large": "japan", "middle": "hokkaido", "small": "sapporo"},
    {"name": "青森県", "large": "japan", "middle": "aomori", "small": "aomori"},
    {"name": "岩手県", "large": "japan", "middle": "iwate", "small": "morioka"},
    {"name": "宮城県", "large": "japan", "middle": "miyagi", "small": "sendai"},
    {"name": "秋田県", "large": "japan", "middle": "akita", "small": "akita"},
    {"name": "山形県", "large": "japan", "middle": "yamagata", "small": "yamagata"},
    {"name": "福島県", "large": "japan", "middle": "fukushima", "small": "fukushima"},
    {"name": "東京都", "large": "japan", "middle": "tokyo", "small": "tokyo"},
    {"name": "神奈川県", "large": "japan", "middle": "kanagawa", "small": "yokohama"},
    {"name": "千葉県", "large": "japan", "middle": "chiba", "small": "chiba"},
]

# ===============================
# 宿泊検索（検索フォーム）
# ===============================
@app.route("/stay_search", methods=["GET"])
def stay_search():
    return render_template("stay_search.html", prefectures=PREFECTURES)

# ===============================
# 宿泊検索結果
# ===============================
@app.route("/stay_search_results", methods=["GET"])
def stay_search_results():

    # HTML から受け取り
    large = request.args.get("large")
    middle = request.args.get("middle")
    small = request.args.get("small")
    checkin_date = request.args.get("checkin_date")
    checkout_date = request.args.get("checkout_date")
    adults = request.args.get("adults", 1)

    url = "https://app.rakuten.co.jp/services/api/Travel/VacantHotelSearch/20170426"

    params = {
        "applicationId": RAKUTEN_API_KEY,
        "format": "json",
        "largeClassCode": large,
        "middleClassCode": middle,
        "smallClassCode": small,
        "checkinDate": checkin_date,
        "checkoutDate": checkout_date,
        "adultNum": adults,
        "hits": 20,
        "page": 1,
        "sort": "+roomCharge"
    }

    response = requests.get(url, params=params)
    data = response.json()

    hotels = data.get("hotels", [])
    error = data.get("error")

    # デバッグ表示（必要なら）
    print("URL:", response.url)
    print("DATA:", data)

    return render_template(
        "stay_search_results.html",
        hotels=hotels,
        error=error,
        checkin_date=checkin_date,
        checkout_date=checkout_date,
        adults=adults,
    )

# ===============================================================
# イベント検索
# ===============================================================

@app.route('/event-search', methods=['GET'])
def event_search():
    return render_template('event_search.html')

@app.route('/event-search-results', methods=['POST'])
def event_search_results():
    keyword = request.form.get('keyword', '').strip()

    # キーワードを含むものを検索
    results = []
    for s in EVENT_DATA:
        if keyword in s["name"] or keyword in s["address"] or keyword in s["category"]:
            results.append(s)

    return render_template(
        "event_search_results.html",
        keyword=keyword,
        results=results
    )

# ============================
# 天気（Open-Meteo）
# ============================

import requests

# ======================================
# 都道府県 → 緯度経度
# ======================================

PREF_LATLON = {
    "北海道": (43.06417, 141.34694),
    "青森県": (40.82444, 140.74),
    "岩手県": (39.70361, 141.1525),
    "宮城県": (38.26889, 140.87194),
    "秋田県": (39.71861, 140.1025),
    "山形県": (38.24056, 140.36333),
    "福島県": (37.75, 140.46778),
    "茨城県": (36.34139, 140.44667),
    "栃木県": (36.56583, 139.88361),
    "群馬県": (36.39111, 139.06083),
    "埼玉県": (35.85694, 139.64889),
    "千葉県": (35.60472, 140.12333),
    "東京都": (35.68944, 139.69167),
    "神奈川県": (35.44778, 139.6425),
    "新潟県": (37.90222, 139.02361),
    "富山県": (36.69528, 137.21139),
    "石川県": (36.59444, 136.62556),
    "福井県": (36.06528, 136.22194),
    "山梨県": (35.66389, 138.56833),
    "長野県": (36.65139, 138.18111),
    "岐阜県": (35.39111, 136.72222),
    "静岡県": (34.97694, 138.38306),
    "愛知県": (35.18028, 136.90667),
    "三重県": (34.73028, 136.50861),
    "滋賀県": (35.00444, 135.86833),
    "京都府": (35.02139, 135.75556),
    "大阪府": (34.68639, 135.52),
    "兵庫県": (34.69139, 135.18306),
    "奈良県": (34.68528, 135.83278),
    "和歌山県": (34.22611, 135.1675),
    "鳥取県": (35.50361, 134.23833),
    "島根県": (35.47222, 133.05056),
    "岡山県": (34.66167, 133.935),
    "広島県": (34.39639, 132.45944),
    "山口県": (34.18583, 131.47139),
    "徳島県": (34.06583, 134.55944),
    "香川県": (34.34028, 134.04333),
    "愛媛県": (33.84167, 132.76611),
    "高知県": (33.55972, 133.53111),
    "福岡県": (33.59028, 130.40194),
    "佐賀県": (33.24944, 130.29889),
    "長崎県": (32.74472, 129.87361),
    "熊本県": (32.78972, 130.74167),
    "大分県": (33.23806, 131.6125),
    "宮崎県": (31.91111, 131.42389),
    "鹿児島県": (31.56028, 130.55806),
    "沖縄県": (26.2125, 127.68111),
}

# ======================================
# 天気（Open-Meteo + アイコン + 週間予報）
# ======================================

import requests

def convert_weather_icon(code):
    if code == 0: return "☀️"
    if code == 1: return "🌤"
    if code == 2: return "⛅"
    if code == 3: return "☁️"
    if code in [45, 48]: return "🌫"
    if code in [51, 53, 55]: return "🌧"
    if code in [61, 63, 65]: return "🌧"
    if code in [66, 67]: return "🌧❄️"
    if code in [71, 73, 75]: return "❄️"
    if code == 77: return "🌨"
    if code in [80, 81, 82]: return "🌦"
    if code in [85, 86]: return "🌨"
    if code == 95: return "⛈️"
    if code in [96, 99]: return "⛈️"
    return "❓"

@app.route('/weather', methods=['GET', 'POST'])
def weather():
    weather_data = None
    weekly = None
    error = None

    if request.method == "POST":
        pref = request.form.get("prefecture")

        if pref not in PREF_LATLON:
            error = "都道府県を選択してください。"
        else:
            lat, lon = PREF_LATLON[pref]

            url = (
                "https://api.open-meteo.com/v1/forecast"
                f"?latitude={lat}&longitude={lon}"
                "&current_weather=true"
                "&daily=weathercode,temperature_2m_max,temperature_2m_min,precipitation_probability_max"
                "&timezone=Asia/Tokyo"
            )

            try:
                res = requests.get(url).json()

                # 現在の天気
                code = res["current_weather"]["weathercode"]

                weather_data = {
                    "city_name": pref,
                    "description": "現在の天気",
                    "temp": res["current_weather"]["temperature"],
                    "humidity": "-",  # ※後で時間別を追加できる
                    "icon": convert_weather_icon(code),
                }

                # 週間データ
                weekly = []
                for i in range(7):
                    w_code = res["daily"]["weathercode"][i]
                    weekly.append({
                        "date": res["daily"]["time"][i],
                        "icon": convert_weather_icon(w_code),
                        "max": res["daily"]["temperature_2m_max"][i],
                        "min": res["daily"]["temperature_2m_min"][i],
                        "precip": res["daily"]["precipitation_probability_max"][i],
                    })

            except Exception as e:
                print(e)
                error = "天気データの取得に失敗しました。"

    return render_template(
        "weather.html",
        weather=weather_data,
        weekly=weekly,
        error=error,
        prefectures=list(PREF_LATLON.keys())
    )

# ===============================================================
# アプリ起動
# ===============================================================
if __name__ == '__main__':
    app.run(debug=True)
