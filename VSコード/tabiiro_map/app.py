from flask import Flask, render_template, jsonify

app = Flask(__name__)

# --- ルーティング ---

# ホーム画面を表示するルーティング
@app.route('/')
def home():
    # home.htmlをレンダリング（base.htmlが自動で適用される）
    return render_template('home.html')

# アカウント情報画面のルーティング（base.htmlでurl_for('user_data')として参照されている）
@app.route('/user-data')
def user_data():
    # 実際には別のテンプレートをレンダリングします
    return "<h1>アカウント情報ページ</h1>"

# --- APIエンドポイント ---

# 地図の色付けデータを提供するAPIエンドポイント
@app.route('/api/travel-records')
def travel_records_api():
    # ⚠️ 注意: ここにデータベースからデータを取得するロジックを実装してください。
    
    # 仮のデータ (都道府県ID 'prefXX' とステータス)
    data = {
        'pref13': {'status': 'visited', 'count': 5},    # 東京都
        'pref27': {'status': 'want_to_go', 'count': 2}, # 大阪府
        'pref40': {'status': 'visited', 'count': 8},    # 福岡県
        'pref01': {'status': 'visited', 'count': 1},    # 北海道
        'pref22': {'status': 'want_to_go', 'count': 3}  # 静岡県
    }
    return jsonify(data)

if __name__ == '__main__':
    # 開発用サーバーを実行
    app.run(debug=True)