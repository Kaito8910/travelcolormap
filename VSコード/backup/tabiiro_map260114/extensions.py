# extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# アプリ本体とは別にインスタンスだけ用意しておく
db = SQLAlchemy()
migrate = Migrate()
