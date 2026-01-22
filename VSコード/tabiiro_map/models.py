# models.py
from datetime import datetime
from extensions import db

# ============================
# ユーザーテーブル（USER）
# ============================
class User(db.Model):
    __tablename__ = "USER"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 主キー
    username = db.Column(db.String(30), unique=True, nullable=False)  # ユーザー名
    email = db.Column(db.String(100), unique=True, nullable=False)    # メールアドレス
    password = db.Column(db.String(200), nullable=False)              # ハッシュ済みパスワード
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)  # 作成日時
    updated_at = db.Column(
        db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False
    )  # 更新日時

# ============================
# 観光地テーブル（SPOT）
# ============================
class Spot(db.Model):
    __tablename__ = "SPOT"

    spot_id = db.Column(db.Integer, primary_key=True, autoincrement=True)          # 観光地ID
    user_id = db.Column(db.Integer, db.ForeignKey("USER.id"), nullable=False)      # 登録ユーザー
    name = db.Column(db.String(100), nullable=False)                               # 観光地名
    prefecture = db.Column(db.String(20), nullable=False)                          # 都道府県（短縮名：東京/京都など）
    visit_date = db.Column(db.Date, nullable=False)                                # 訪問日
    comment = db.Column(db.Text)                                                   # コメント
    weather = db.Column(db.String(50))                                             # 天気アイコン（☀️など）
    temp_max = db.Column(db.Float)                                                 # 最高気温
    temp_min = db.Column(db.Float)                                                 # 最低気温
    precipitation = db.Column(db.Float)                                            # 降水量
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)      # 作成日時
    updated_at = db.Column(
        db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False
    )  # 更新日時

    # SPOT から Photo への参照（spot.photos で取得できる）
    photos = db.relationship("Photo", backref="spot", cascade="all, delete", lazy=True)

# ============================
# グルメテーブル（FOOD）
# ============================
class Food(db.Model):
    __tablename__ = "FOOD"

    food_id = db.Column(db.Integer, primary_key=True, autoincrement=True)          # グルメID
    user_id = db.Column(db.Integer, db.ForeignKey("USER.id"), nullable=False)      # 登録ユーザー
    shop_name = db.Column(db.String(100), nullable=False)                          # 店舗名
    food_name = db.Column(db.String(100))                                          # 料理名
    visit_date = db.Column(db.Date, nullable=False)                                # 訪問日
    evaluation = db.Column(db.Integer)                                             # 評価（1〜5）
    memo = db.Column(db.Text)                                                      # コメント
    stay_id = db.Column(db.Integer, db.ForeignKey("STAY.stay_id"))                 # 宿泊記録との紐付け（任意）
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)      # 作成日時
    updated_at = db.Column(
        db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False
    )  # 更新日時

    # FOOD → Photo（food.photos で取得可能）
    photos = db.relationship("Photo", backref="food", cascade="all, delete", lazy=True)

# ============================
# 宿泊テーブル（STAY）
# ============================
class Stay(db.Model):
    __tablename__ = "STAY"

    stay_id = db.Column(db.Integer, primary_key=True, autoincrement=True)          # 宿泊ID
    user_id = db.Column(db.Integer, db.ForeignKey("USER.id"), nullable=False)      # 登録ユーザー
    hotel_name = db.Column(db.String(100), nullable=False)                         # 宿名
    checkin_date = db.Column(db.Date, nullable=False)                              # チェックイン日
    checkout_date = db.Column(db.Date, nullable=False)                             # チェックアウト日
    price = db.Column(db.Integer)                                                  # 料金
    memo = db.Column(db.Text)                                                      # メモ
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)      # 作成日時
    updated_at = db.Column(
        db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False
    )  # 更新日時

# ============================
# ブックマークテーブル（BOOKMARK）
# ============================
class Bookmark(db.Model):
    __tablename__ = "BOOKMARK"

    bookmark_id = db.Column(db.Integer, primary_key=True, autoincrement=True)      # ブックマークID
    user_id = db.Column(db.Integer, db.ForeignKey("USER.id"), nullable=False)      # ユーザーID
    target_type = db.Column(db.String(30), nullable=False)                         # 種別（spot/hotel/event など）
    target_id = db.Column(db.String(50), nullable=False)                           # 対象のID
    title = db.Column(db.String(100))                                              # 表示タイトル
    thumb = db.Column(db.String(255))                                              # サムネURL or ファイル名
    detail_url = db.Column(db.String(500))                                         # 詳細ページURL（外部リンクも可）
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)      # 登録日時

# ============================
# 写真テーブル（PHOTO）
# ============================
class Photo(db.Model):
    __tablename__ = "PHOTO"

    photo_id = db.Column(db.Integer, primary_key=True, autoincrement=True)         # 写真ID
    user_id = db.Column(db.Integer, db.ForeignKey("USER.id"), nullable=False)      # 所有ユーザー
    spot_id = db.Column(db.Integer, db.ForeignKey("SPOT.spot_id"))                 # 観光地紐付け
    food_id = db.Column(db.Integer, db.ForeignKey("FOOD.food_id"))                 # グルメ紐付け
    stay_id = db.Column(db.Integer, db.ForeignKey("STAY.stay_id"))                 # 宿泊紐付け
    filename = db.Column(db.String(255), nullable=False)                           # static/uploads 内のファイル名
    uploaded_at = db.Column(db.DateTime, default=datetime.now, nullable=False)     # アップロード日時

# ============================
# 都道府県別訪問回数（TRAVEL_RECORD）
# ============================
class TravelRecord(db.Model):
    __tablename__ = "TRAVEL_RECORD"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)               # 主キー
    user_id = db.Column(db.Integer, db.ForeignKey("USER.id"), nullable=False)      # ユーザー
    prefecture = db.Column(db.String(20), nullable=False)                          # 都道府県（短縮形：東京/京都など）
    visit_count = db.Column(db.Integer, nullable=False, default=0)                 # 訪問回数
#==============================
# イベントテーブル（EVENTS）
#==============================
class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    month = db.Column(db.Integer)
    city = db.Column(db.String(100))
    url = db.Column(db.String(500))
    pref_code = db.Column(db.String(10))     
    pref_name = db.Column(db.String(50))
    category = db.Column(db.String(50))
    description = db.Column(db.Text)
