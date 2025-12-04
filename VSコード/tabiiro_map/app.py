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
from datetime import datetime, date, timedelta
import json

def load_spots_json():
    json_path = os.path.join(app.root_path, "static", "json", "spots.json")
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)
    
def load_events_json():
    json_path = os.path.join(app.root_path, "static", "json", "events.json")
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)
    
def get_prefecture_list():
    data = load_spots_json()
    return [p["pref_name_ja"] for p in data]

def extract_hotel_info(raw_hotels):
    hotels = []
    for wrapper in raw_hotels:
        if isinstance(wrapper, list) and len(wrapper) > 0:
            info = wrapper[0].get("hotelBasicInfo", {})
            hotels.append(info)
    return hotels


app = Flask(__name__)
app.secret_key = 'your_secret_key'

# JSON をロード
SPOTS_JSON = load_spots_json()
EVENTS_JSON = load_events_json()



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
    photos = db.relationship("Photo", backref="spot", cascade="all, delete", lazy=True)
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
    photos = db.relationship("Photo", backref="food", cascade="all, delete", lazy=True)
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
    detail_url = db.Column(db.String(500))

# ---------------------------------------------------------------
# 写真テーブル（PHOTO）
# ---------------------------------------------------------------
class Photo(db.Model):
    __tablename__ = "PHOTO"

    photo_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("USER.id"), nullable=False)
    spot_id = db.Column(db.Integer, db.ForeignKey("SPOT.spot_id"))
    food_id = db.Column(db.Integer, db.ForeignKey("FOOD.food_id"))
    stay_id = db.Column(db.Integer, db.ForeignKey("STAY.stay_id"))
    filename = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

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
@app.route('/spot_register', methods=['GET', 'POST'])
def spot_register():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        user_id = session.get('user_id')

        # --- フォームデータ ---
        spot_name = request.form.get("spot_name")
        pref_full = request.form.get("prefecture")
        visit_date_str = request.form.get('visit_date')
        comment = request.form.get('comment')

        if not spot_name:
            flash("観光地名を入力してください。", "error")
            return redirect(url_for('spot_register'))

        if not pref_full:
            flash("都道府県を選択してください。", "error")
            return redirect(url_for('spot_register'))

        # 都道府県名を短縮
        if pref_full == "北海道":
            pref_short = "北海道"
        else:
            pref_short = pref_full.replace("都", "").replace("府", "").replace("県", "")

        # 日付変換
        visit_date = datetime.strptime(visit_date_str, "%Y-%m-%d").date()

        # --- 天気API ---
        lat, lon = PREF_LATLON.get(pref_short, (None, None))
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
            except Exception as e:
                print("天気取得失敗:", e)

        # --- Spot を保存（ここでは「写真なし」で保存） ---
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
        db.session.flush()  # ★ spot_id を取得するため必須！

        # --- 写真複数保存 ---
        photos = request.files.getlist("photos[]")
        upload_dir = os.path.join("static", "uploads")
        os.makedirs(upload_dir, exist_ok=True)

        for p in photos:
            if not p or not p.filename:
                continue
            
            filename = f"{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{p.filename}"
            p.save(os.path.join(upload_dir, filename))

            # Photo レコード作成
            new_photo = Photo(
                user_id=user_id,
                spot_id=new_spot.spot_id,
                filename=filename
            )
            db.session.add(new_photo)

        # --- DB確定 ---
        db.session.commit()

        flash("観光地を登録しました！（写真・天気データ含む）", "success")
        return redirect(url_for('spot_list'))

    return render_template("spot_register.html")

# ===============================================================
# グルメ記録一覧
# ===============================================================
@app.route('/gourmet_list')
def gourmet_list():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    foods = Food.query.filter_by(user_id=user_id).all()

    # 店舗名 → 記録一覧
    grouped = {}
    for f in foods:
        grouped.setdefault(f.shop_name, [])
        grouped[f.shop_name].append(f)

    # 店舗ごとの平均評価を計算
    shop_summary = []
    for shop, items in grouped.items():
        avg = sum(i.evaluation for i in items) / len(items)

        # 写真は代表として1枚（最新のにする）
        # 写真は代表として1枚（最新の）
        thumbnail = None
        if items and items[0].photos:
            thumbnail = items[0].photos[-1].filename

        shop_summary.append({
            "shop_name": shop,
            "items": items,
            "avg": round(avg, 1),   # 小数1桁
            "count": len(items),
            "thumbnail": thumbnail
        })

    return render_template(
        'gourmet_list.html',
        shop_summary=shop_summary
    )

# ===============================================================
# グルメ記録店舗詳細
# ===============================================================

@app.route('/shop/<shop_name>')
def shop_detail(shop_name):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    user_id = session.get('user_id')

    items = Food.query.filter_by(user_id=user_id, shop_name=shop_name).all()

    if not items:
        flash("データが存在しません。", "error")
        return redirect(url_for('gourmet_list'))

    avg = sum(i.evaluation for i in items) / len(items)
    avg = round(avg, 1)

    # サムネイル
    thumbnail = None
    for f in items:
        if f.photos:
            thumbnail = f.photos[-1].filename
            break


    return render_template(
        'shop_detail.html',
        shop_name=shop_name,
        items=items,
        avg=avg,
        count=len(items),
        thumbnail=thumbnail
    )


# ===============================================================
#グルメ記録登録
# ===============================================================

@app.route('/gourmet_record')
def gourmet_record():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('gourmet_record.html')


# ===============================================================
# グルメ記録追加（POST処理）
# ===============================================================
@app.route('/add_gourmet', methods=['POST'])
def add_gourmet():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    user_id = session.get('user_id')

    shop_name = request.form.get('shop_name')
    food_name = request.form.get('food_name')
    visit_date = request.form.get('visit_date')
    evaluation = int(request.form.get('evaluation'))
    memo = request.form.get('memo')

    visit_date = datetime.strptime(visit_date, "%Y-%m-%d").date()

    # ----------- グルメ記録本体を先に保存 -----------
    new_food = Food(
        user_id=user_id,
        shop_name=shop_name,
        food_name=food_name,
        visit_date=visit_date,
        evaluation=evaluation,
        memo=memo
    )

    db.session.add(new_food)
    db.session.flush()  # ★ food_idを取得するため必須！

    # ----------- 写真複数アップロード -----------
    upload_dir = os.path.join("static", "uploads")
    os.makedirs(upload_dir, exist_ok=True)

    photos = request.files.getlist("photos[]")  # ★ 複数取得

    for p in photos:
        if not p.filename:
            continue

        filename = (
            f"{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{p.filename}"
        )
        p.save(os.path.join(upload_dir, filename))

        new_photo = Photo(
            user_id=user_id,
            food_id=new_food.food_id,
            filename=filename
        )
        db.session.add(new_photo)

    db.session.commit()

    flash("グルメ記録を登録しました！", "success")
    return redirect(url_for('gourmet_list'))

# ===============================================================
# グルメ記録更新
# ===============================================================
@app.route('/gourmet_edit/<int:food_id>', methods=['GET', 'POST'])
def gourmet_edit(food_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    food = Food.query.get_or_404(food_id)

    if request.method == 'POST':
        food.shop_name = request.form.get('shop_name')
        food.food_name = request.form.get('food_name')
        food.evaluation = int(request.form.get('evaluation'))
        food.memo = request.form.get('memo')

        # ★ visit_date が文字列で来るので必ず変換
        visit_date_str = request.form.get('visit_date')
        food.visit_date = datetime.strptime(visit_date_str, "%Y-%m-%d").date()

        # ----- 写真追加 -----
        upload_dir = os.path.join("static", "uploads")
        os.makedirs(upload_dir, exist_ok=True)

        photos = request.files.getlist("photos[]")
        for p in photos:
            if not p.filename:
                continue

            filename = f"{food.user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{p.filename}"
            p.save(os.path.join(upload_dir, filename))

            new_photo = Photo(
                user_id=food.user_id,
                food_id=food.food_id,
                filename=filename
            )
            db.session.add(new_photo)

        db.session.commit()

        flash("グルメ記録を更新しました！", "success")

        # ★ ここを必ず修正
        return redirect(url_for('gourmet_detail', food_id=food.food_id))

    return render_template('gourmet_edit.html', food=food)

# ===============================================================
# グルメ記録詳細
# ===============================================================

@app.route('/gourmet_detail/<int:food_id>')
def gourmet_detail(food_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    food = Food.query.get_or_404(food_id)

    # 同じ店舗の記録一覧を取得
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

# ===============================================================
# グルメ記録削除
# ===============================================================
@app.route('/gourmet_delete/<int:food_id>', methods=['POST'])
def gourmet_delete(food_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    food = Food.query.get_or_404(food_id)

    db.session.delete(food)
    db.session.commit()

    flash("グルメ記録を削除しました。", "success")
    return redirect(url_for('gourmet_list'))

@app.route('/delete_food_photo/<int:photo_id>', methods=['POST'])
def delete_food_photo(photo_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    photo = Photo.query.get_or_404(photo_id)
    user_id = session.get('user_id')

    # 他人の写真は削除不可
    if photo.user_id != user_id:
        flash("削除権限がありません。", "error")
        return redirect(url_for('gourmet_list'))

    # 写真ファイルのパス
    file_path = os.path.join("static", "uploads", photo.filename)

    # ファイルが存在すれば削除
    if os.path.exists(file_path):
        os.remove(file_path)

    # photo レコード削除
    db.session.delete(photo)
    db.session.commit()

    flash("写真を削除しました！", "success")

    # 元の編集画面へリダイレクト
    return redirect(url_for('gourmet_edit', food_id=photo.food_id))


# ===============================================================
# スポット一覧
# ===============================================================
@app.route('/spot_list', methods=['GET'])
def spot_list():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    selected_pref = request.args.get('prefecture', '')

    # 都道府県リスト（spot_register と統一）
    PREF_LIST = [
        "北海道","青森県","岩手県","宮城県","秋田県","山形県","福島県",
        "茨城県","栃木県","群馬県","埼玉県","千葉県","東京都","神奈川県",
        "新潟県","富山県","石川県","福井県","山梨県","長野県","岐阜県",
        "静岡県","愛知県","三重県","滋賀県","京都府","大阪府","兵庫県",
        "奈良県","和歌山県","鳥取県","島根県","岡山県","広島県","山口県",
        "徳島県","香川県","愛媛県","高知県","福岡県","佐賀県","長崎県",
        "熊本県","大分県","宮崎県","鹿児島県","沖縄県"
    ]

    # --- 絞り込みあり ---
    if selected_pref:
        spots = Spot.query.filter_by(
            user_id=user_id, prefecture=selected_pref
        ).order_by(
            Spot.prefecture.asc(), Spot.name.asc()
        ).all()
    else:
        # --- 全件表示 ---
        spots = Spot.query.filter_by(user_id=user_id).order_by(
            Spot.prefecture.asc(), Spot.name.asc()
        ).all()

    return render_template(
        'spot_list.html',
        spots=spots,
        prefectures=PREF_LIST,
        selected_pref=selected_pref
    )

# ===============================================================
# スポット一覧詳細
# ===============================================================
@app.route('/spot/<int:spot_id>')
def spot_detail(spot_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    spot = Spot.query.get_or_404(spot_id)
    return render_template('spot_detail.html', spot=spot)

# ===============================================================
# スポット編集
# ==============================================================
@app.route('/spot_edit/<int:spot_id>', methods=['GET', 'POST'])
def spot_edit(spot_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    spot = Spot.query.get_or_404(spot_id)

    # 都道府県のリスト（spot_register と合わせる）
    prefectures = [
        "北海道","青森県","岩手県","宮城県","秋田県","山形県","福島県",
        "茨城県","栃木県","群馬県","埼玉県","千葉県","東京都","神奈川県",
        "新潟県","富山県","石川県","福井県","山梨県","長野県",
        "岐阜県","静岡県","愛知県","三重県",
        "滋賀県","京都府","大阪府","兵庫県","奈良県","和歌山県",
        "鳥取県","島根県","岡山県","広島県","山口県",
        "徳島県","香川県","愛媛県","高知県",
        "福岡県","佐賀県","長崎県","熊本県","大分県","宮崎県","鹿児島県",
        "沖縄県"
    ]

    if request.method == 'POST':
        spot.name = request.form.get('spot_name')
        prefecture_full = request.form.get('prefecture')

        # 北海道以外の都道府県は短縮する
        if prefecture_full == "北海道":
            spot.prefecture = "北海道"
        else:
            spot.prefecture = prefecture_full.replace("都","").replace("府","").replace("県","")

        visit_date_str = request.form.get('visit_date')
        spot.visit_date = datetime.strptime(visit_date_str, "%Y-%m-%d").date()

        spot.comment = request.form.get('comment')

        # --- 写真追加 ---
        photos = request.files.getlist('photos[]')
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
        return redirect(url_for('spot_detail', spot_id=spot.spot_id))

    return render_template('spot_edit.html', spot=spot, prefectures=prefectures)

@app.route('/delete_spot_photo/<int:photo_id>', methods=['POST'])
def delete_spot_photo(photo_id):
    if not session.get('logged_in'):
        return "Unauthorized", 401

    photo = Photo.query.get_or_404(photo_id)

    # ファイル削除
    filepath = os.path.join("static", "uploads", photo.filename)
    if os.path.exists(filepath):
        os.remove(filepath)

    db.session.delete(photo)
    db.session.commit()

    return "OK", 200

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
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({})

    # ログインユーザーの観光地のみ取得
    spots = Spot.query.filter_by(user_id=user_id).all()

    pref_counts = {}

    for spot in spots:
        pref = spot.prefecture.strip()  # 念のためスペース除去
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
# API — ユーザー訪問データ
# ===============================================================

@app.route('/api/visit_data')
def api_visit_data():
    if not session.get('logged_in'):
        return jsonify({})  # ログインしてない場合は空を返す

    user_id = session.get('user_id')

    # DBからユーザーのスポット取得
    spots = Spot.query.filter_by(user_id=user_id).all()

    pref_counts = {}

    for spot in spots:
        pref = spot.prefecture  # short_pref（例：東京）
        pref_counts[pref] = pref_counts.get(pref, 0) + 1

    return jsonify(pref_counts)


# ===============================================================
# スポット検索
# ===============================================================

# ==== 検索フォーム ====
@app.route("/spot_search")
def spot_search():
    prefectures = get_prefecture_list()
    return render_template("spot_search.html", prefectures=prefectures)



# ==== 検索結果 ====
@app.route("/spot_search_results")
def spot_search_results():
    prefecture = request.args.get("prefecture", "")
    keyword = request.args.get("keyword", "").lower().strip()

    data = load_spots_json()

    # 関数で都道府県一覧を取得
    prefectures = get_prefecture_list()

    results = []
    for pref in data:
        pref_name = pref.get("pref_name_ja", "")
        spots = pref.get("spots", [])

        if prefecture and pref_name != prefecture:
            continue

        for s in spots:

            text = (
                s.get("spot_name", "") +
                s.get("city", "") +
                s.get("category", "") +
                s.get("description", "")
            ).lower()

            if keyword and keyword not in text:
                continue

            results.append({
                "spot_name": s.get("spot_name", ""),
                "city": s.get("city", ""),
                "category": s.get("category", ""),
                "description": s.get("description", ""),
                "pref_name": pref_name
            })

    return render_template(
        "spot_search_results.html",
        results=results,
        prefectures=prefectures
    )


# ===============================================================
# 宿泊検索
# ===============================================================

APPLICATION_ID = "1002136947918553343"

def search_hotels(keyword, page=1, hits=20):
    url = "https://app.rakuten.co.jp/services/api/Travel/KeywordHotelSearch/20170426"
    params = {
        "applicationId": APPLICATION_ID,
        "format": "json",
        "keyword": keyword,
        "page": page,
        "hits": hits,
        "formatVersion": 2  # ネスト浅めの形式
    }
    resp = requests.get(url, params=params)
    data = resp.json()
    return data.get("hotels", [])

@app.route("/hotel_search", methods=["GET", "POST"])
def hotel_search():
    if request.method == "POST":
        kw = request.form.get("keyword", "").strip()
        if not kw:
            return render_template("hotel_search.html", error="キーワードを入力してください")
        return redirect(url_for("hotel_results", keyword=kw))
    return render_template("hotel_search.html")

@app.route("/hotel_results/<keyword>")
def hotel_results(keyword):
    user_id = session.get("user_id")

    # API 結果取得（ネストされた raw データ）
    raw_hotels = search_hotels(keyword)

    # hotelBasicInfo だけを取り出してフラットにする
    hotels = extract_hotel_info(raw_hotels)

    # すでにブックマークされているID取得
    bookmarked = Bookmark.query.filter_by(
        user_id=user_id,
        target_type="hotel"
    ).all()
    bookmarked_ids = {str(bm.target_id) for bm in bookmarked}

    # フラグ追加
    for h in hotels:
        hotel_id = str(h.get("hotelNo"))
        h["is_bookmarked"] = hotel_id in bookmarked_ids

    return render_template("hotel_results.html",
                            hotels=hotels,
                            keyword=keyword)


# ===============================================================
# イベント検索
# ===============================================================
CONNPASS_API_URL = "https://connpass.com/api/v2/events/"
API_TOKEN = "k0ojDAFr.NMjNt9vSGq9tjmx4JeKQQ6U97tkLSH7RRJNGgyCcUbo1U6Xi8lWIw7oc"

@app.route('/event-search-results')
def event_search_results():
    prefecture = request.args.get("prefecture", "")
    month = request.args.get("month", "")
    period = request.args.get("period", "")  # 上旬/中旬/下旬
    keyword = request.args.get("keyword", "").strip()

    results = []

    for pref in EVENTS_JSON:
        pref_name = pref["pref_name_ja"]

        # 都道府県フィルタ
        if prefecture and pref_name != prefecture:
            continue

        for ev in pref["events"]:
            ev_month_full = ev.get("month", "")  # 例: "8月上旬"

            # === 月の抽出 ===
            ev_month_num = ""
            for n in range(1, 13):
                if f"{n}月" in ev_month_full:
                    ev_month_num = str(n)
                    break

            # 月フィルタ
            if month and month != ev_month_num:
                continue

            # 旬フィルタ
            if period and period not in ev_month_full:
                continue

            # キーワードフィルタ
            if keyword:
                if (keyword not in ev.get("event_name", "")) and \
                    (keyword not in ev.get("description", "")):
                    continue

            results.append({
                "event_id": ev.get("event_id", ""),          # ★追加
                "event_name": ev.get("event_name", ""),
                "month": ev.get("month", ""),
                "city": ev.get("city", ""),
                "category": ev.get("category", ""),
                "description": ev.get("description", ""),
                "pref_name": pref_name,
                "event_url": ev.get("event_url", "")         # ★追加
            })


    return render_template(
        "event_search_results.html",
        results=results,
        prefectures=[p["pref_name_ja"] for p in EVENTS_JSON],
        months=list(range(1, 13)),
        periods=["上旬", "中旬", "下旬"]
    )

@app.route("/event_search")
def event_search():
    prefectures = get_prefecture_list()
    months = list(range(1, 13))
    periods = ["上旬", "中旬", "下旬"]
    return render_template("event_search.html", prefectures=prefectures, months=months, periods=periods)

@app.route('/event-search1', methods=['GET'])
def event_search1():
    return render_template('event_search1.html')

@app.route('/event-search-results1', methods=['POST'])
def event_search_results1():
    # フォーム入力を取得
    keyword = request.form.get('keyword', '').strip()
    ymd = request.form.get('ymd', '').strip()
    prefecture = request.form.get('prefecture', '').strip()

    # APIパラメータ
    params = {
        "count": 20,
        "order": 1,
    }
    if keyword:
        params["keyword"] = keyword
    if ymd:
        params["ymd"] = ymd
    if prefecture:
        params["prefecture"] = prefecture

    headers = {
        "X-API-Key": API_TOKEN,
        "User-Agent": "PythonApp/1.0"  # ← ここを追加
    }

    try:
        res = requests.get(CONNPASS_API_URL, params=params, headers=headers, timeout=10)
        res.raise_for_status()
        data = res.json()
    except requests.exceptions.HTTPError:
        flash(f"API呼び出しエラー: {res.status_code} {res.reason}", "danger")
        return redirect(url_for('event_search'))
    except requests.exceptions.RequestException as e:
        flash(f"API呼び出しエラー: {e}", "danger")
        return redirect(url_for('event_search'))
    except ValueError as e:
        flash(f"JSON解析エラー: {e}", "danger")
        return redirect(url_for('event_search'))

    events = data.get("events", [])

    return render_template(
        "event_search_results1.html",
        events=events,
        keyword=keyword,
        ymd=ymd,
        prefecture=prefecture
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
    "青森": (40.82444, 140.74),
    "岩手": (39.70361, 141.1525),
    "宮城": (38.26889, 140.87194),
    "秋田": (39.71861, 140.1025),
    "山形": (38.24056, 140.36333),
    "福島": (37.75, 140.46778),
    "茨城": (36.34139, 140.44667),
    "栃木": (36.56583, 139.88361),
    "群馬": (36.39111, 139.06083),
    "埼玉": (35.85694, 139.64889),
    "千葉": (35.60472, 140.12333),
    "東京": (35.68944, 139.69167),
    "神奈川": (35.44778, 139.6425),
    "新潟": (37.90222, 139.02361),
    "富山": (36.69528, 137.21139),
    "石川": (36.59444, 136.62556),
    "福井": (36.06528, 136.22194),
    "山梨": (35.66389, 138.56833),
    "長野": (36.65139, 138.18111),
    "岐阜": (35.39111, 136.72222),
    "静岡": (34.97694, 138.38306),
    "愛知": (35.18028, 136.90667),
    "三重": (34.73028, 136.50861),
    "滋賀": (35.00444, 135.86833),
    "京都": (35.02139, 135.75556),
    "大阪": (34.68639, 135.52),
    "兵庫": (34.69139, 135.18306),
    "奈良": (34.68528, 135.83278),
    "和歌山": (34.22611, 135.1675),
    "鳥取": (35.50361, 134.23833),
    "島根": (35.47222, 133.05056),
    "岡山": (34.66167, 133.935),
    "広島": (34.39639, 132.45944),
    "山口": (34.18583, 131.47139),
    "徳島": (34.06583, 134.55944),
    "香川": (34.34028, 134.04333),
    "愛媛": (33.84167, 132.76611),
    "高知": (33.55972, 133.53111),
    "福岡": (33.59028, 130.40194),
    "佐賀": (33.24944, 130.29889),
    "長崎": (32.74472, 129.87361),
    "熊本": (32.78972, 130.74167),
    "大分": (33.23806, 131.6125),
    "宮崎": (31.91111, 131.42389),
    "鹿児島": (31.56028, 130.55806),
    "沖縄": (26.2125, 127.68111),
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
# ブックマーク一覧
# ===============================================================
@app.route('/bookmark-list', methods=['GET'])
def bookmark_list():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    filter_type = request.args.get('filter', 'all')

    query = Bookmark.query.filter_by(user_id=user_id)
    if filter_type != 'all':
        query = query.filter_by(target_type=filter_type)

    bookmarks = query.all()

    # URLはDBに保存されているものをそのまま使う
    for bm in bookmarks:
        if not bm.detail_url:
            # スポットだけ内部リンクを自動生成
            if bm.target_type == "spot":
                bm.detail_url = url_for("spot_detail", spot_id=bm.target_id)
        # hotel, event は DB の URL をそのまま使用

    return render_template(
        'bookmark_list.html',
        bookmarks=bookmarks,
        filter=filter_type
    )

@app.route('/bookmark/add', methods=['POST'])
def add_bookmark():
    if not session.get('logged_in'):
        return jsonify({"ok": False, "msg": "LOGIN_REQUIRED"})

    user_id = session.get('user_id')
    target_type = request.form.get("type")
    target_id = request.form.get("id")
    title = request.form.get("title")
    thumb = request.form.get("thumb", "")
    detail_url = request.form.get("url", "")   # ★追加

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
        detail_url=detail_url  # ★保存
    )

    db.session.add(new_bm)
    db.session.commit()

    return jsonify({"ok": True})

@app.route('/bookmark/remove', methods=['POST'])
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

@app.route('/bookmark/delete', methods=['POST'])
def bookmark_delete():
    if not session.get('logged_in'):
        flash("ログインしてください", "error")
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    target_type = request.form.get("type")
    target_id = request.form.get("id")

    bm = Bookmark.query.filter_by(
        user_id=user_id,
        target_type=target_type,
        target_id=target_id
    ).first()

    if not bm:
        flash("ブックマークが見つかりません", "error")
        return redirect(url_for('bookmark_list'))

    db.session.delete(bm)
    db.session.commit()

    flash("ブックマークを削除しました", "success")
    return redirect(url_for('bookmark_list'))


# ===============================================================
# アプリ起動
# ===============================================================
if __name__ == '__main__':
    app.run(debug=True)
