# app.py
from flask import Flask
from config import Config
from extensions import db, migrate

# Blueprints を import
from routes.auth import auth_bp
from routes.user import user_bp
from routes.spot import spot_bp
from routes.food import food_bp
from routes.hotel import hotel_bp
from routes.event import event_bp
from routes.bookmark import bookmark_bp
from routes.weather import weather_bp
from routes.api import api_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 拡張の初期化
    db.init_app(app)
    migrate.init_app(app, db)

    # Blueprint 登録
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(spot_bp)
    app.register_blueprint(food_bp)
    app.register_blueprint(hotel_bp)
    app.register_blueprint(event_bp)
    app.register_blueprint(bookmark_bp)
    app.register_blueprint(weather_bp)
    app.register_blueprint(api_bp)

    # ホームだけはここで定義（または home_bp 作っても OK）
    @app.route("/")
    def home():
        from flask import session, render_template
        logged_in = session.get("logged_in", False)
        return render_template("home.html", logged_in=logged_in)

    return app

# flask run / flask routes 用
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
