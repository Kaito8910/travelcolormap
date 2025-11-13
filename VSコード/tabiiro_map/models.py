# models.py
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# ====================================
# アカウント情報管理テーブル
# ====================================
class Account(db.Model):
    __tablename__ = "ACCOUNT"

    # ユーザID（PK, varchar10）
    user_id = db.Column(db.String(10), primary_key=True, nullable=False)

    # ユーザー名
    name = db.Column(db.String(30), nullable=False)

    # メールアドレス（重複不可）
    email = db.Column(db.String(100), nullable=False, unique=True)

    # パスワード（ハッシュ化）
    password = db.Column(db.String(200), nullable=False)

    # 作成日時
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    # 更新日時
    updated_at = db.Column(
        db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False
    )


# ====================================
# 観光地（SPOT）管理テーブル
# ====================================
class Spot(db.Model):
    __tablename__ = "SPOT"

    # 観光地ID
    spot_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # 登録ユーザーID
    user_id = db.Column(db.String(10), db.ForeignKey("ACCOUNT.user_id"), nullable=False)

    # 観光地名
    name = db.Column(db.String(100), nullable=False)

    # 訪問日
    visit_date = db.Column(db.Date, nullable=False)

    # 写真ファイル名
    photo = db.Column(db.String(255))

    # コメント
    comment = db.Column(db.Text)

    # 作成日時
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    # 更新日時
    updated_at = db.Column(
        db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False
    )


# ====================================
# グルメ（FOOD）管理テーブル
# ====================================
class Food(db.Model):
    __tablename__ = "FOOD"

    # グルメ記録ID
    FOOD_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # ユーザーID
    USER_ID = db.Column(db.String(10), db.ForeignKey("ACCOUNT.user_id"), nullable=False)

    # 店舗名
    SHOP_NAME = db.Column(db.String(100), nullable=False)

    # 料理名
    FOOD_NAME = db.Column(db.String(100))

    # 訪問日
    VISIT_DATE = db.Column(db.Date, nullable=False)

    # 評価（1〜5想定）
    EVALUATION = db.Column(db.Integer)

    # メモ
    MEMO = db.Column(db.Text)

    # 宿泊記録ID（紐づけ任意）
    STAY_ID = db.Column(db.Integer, db.ForeignKey("STAY.STAY_ID"))

    # 作成日時
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    # 更新日時
    updated_at = db.Column(
        db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False
    )


# ====================================
# 宿泊（STAY）管理テーブル
# ====================================
class Stay(db.Model):
    __tablename__ = "STAY"

    # 宿泊記録ID
    STAY_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # ユーザーID
    USER_ID = db.Column(db.String(10), db.ForeignKey("ACCOUNT.user_id"), nullable=False)

    # 宿泊施設名
    HOTEL_NAME = db.Column(db.String(100), nullable=False)

    # チェックイン
    CHECKIN_DATE = db.Column(db.Date, nullable=False)

    # チェックアウト
    CHECKOUT_DATE = db.Column(db.Date, nullable=False)

    # 料金
    PRICE = db.Column(db.Integer)

    # メモ
    MEMO = db.Column(db.Text)

    # 作成日時
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    # 更新日時
    updated_at = db.Column(
        db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False
    )


# ====================================
# ブックマーク（BOOKMARK）管理テーブル
# APIデータにも対応
# ====================================
class Bookmark(db.Model):
    __tablename__ = "BOOKMARK"

    # ブックマークID
    BOOKMARK_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # ユーザーID
    USER_ID = db.Column(db.String(10), db.ForeignKey("ACCOUNT.user_id"), nullable=False)

    # 種別：SPOT / FOOD / STAY / API_SPOT / API_HOTEL など
    TARGET_TYPE = db.Column(db.String(30), nullable=False)

    # 対象ID（内部ID も API ID も対応）
    TARGET_ID = db.Column(db.String(50), nullable=False)

    # 表示用タイトル（APIデータで便利）
    TITLE = db.Column(db.String(100))

    # サムネURL（APIデータで便利）
    THUMB = db.Column(db.String(255))

    # 作成日時
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
