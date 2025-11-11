from flask import Flask, render_template, jsonify

app = Flask(__name__)

# --- ルーティング ---

# ホーム画面 (日本地図表示)
@app.route('/')
def home():
    return render_template('home.html')

# アカウント情報画面 (url_for('user_data')に対応)
@app.route('/user-data')
def user_data():
    return "<h1>アカウント情報ページ</h1>"

# 旅行先記録画面 (メニュー項目に対応)
@app.route('/travel-record')
def travel_record():
    return "<h1>旅行先記録ページ</h1>"

# グルメ記録画面 (メニュー項目に対応)
@app.route('/gourmet-record')
def gourmet_record():
    return "<h1>グルメ記録ページ</h1>"

# 宿泊検索画面 (メニュー項目に対応)
@app.route('/stay-search')
def stay_search():
    return "<h1>宿泊検索ページ</h1>"

# イベント検索画面 (メニュー項目に対応)
@app.route('/event-search')
def event_search():
    return "<h1>イベント検索ページ</h1>"

# ログアウトルーティング (メニュー項目に対応)
@app.route('/logout')
def logout():
    return "<h1>ログアウトしました</h1>"


# --- APIエンドポイント ---

# 地図の色付けデータを提供するAPIエンドポイント
@app.route('/api/travel-records')
def travel_records_api():
    # 仮のデータ (Japan Mapが期待する形式: ID 'prefXX' とステータス)
    data = {
        'pref13': {'status': 'visited', 'count': 5},    # 東京都
        'pref27': {'status': 'want_to_go', 'count': 2}, # 大阪府
        'pref40': {'status': 'visited', 'count': 8},    # 福岡県
        'pref01': {'status': 'visited', 'count': 1},    # 北海道
        'pref22': {'status': 'want_to_go', 'count': 3}  # 静岡県
    }
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)