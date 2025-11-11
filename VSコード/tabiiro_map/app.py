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

#--- イベント検索画面 ---
from flask import Flask, render_template, request
import requests
import datetime

app = Flask(__name__)

# === APIキーを設定 ===
JARAN_API_KEY = "7e7c8f15291d905e"
WEATHER_API_KEY = "YOUR_OPENWEATHER_API_KEY"

# === じゃらんAPIベースURL ===
JARAN_URL = "https://webservice.recruit.co.jp/ab-event/v1/"

# === OpenWeatherMap API URL ===
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"

@app.route('/')
def index():
    return render_template('event_search.html', events=None)

@app.route('/search', methods=['POST'])
def search():
    keyword = request.form.get('keyword', '')
    
    # --- じゃらんイベントAPI呼び出し ---
    params = {
        'key': JARAN_API_KEY,
        'keyword': keyword,
        'format': 'json',
        'count': 5
    }
    response = requests.get(JARAN_URL, params=params)
    events = []
    
    if response.status_code == 200:
        data = response.json()
        if 'results' in data and 'event' in data['results']:
            for e in data['results']['event']:
                name = e.get('event_name', '不明なイベント')
                start_date = e.get('event_start_date', '')
                end_date = e.get('event_end_date', '')
                location = e.get('event_place', '')
                summary = e.get('event_caption', '')[:100] + "..."
                
                # --- 天気予報を取得（都市名から） ---
                weather_info = get_weather(location)
                
                events.append({
                    'name': name,
                    'period': f"{start_date} ～ {end_date}",
                    'location': location,
                    'summary': summary,
                    'weather': weather_info
                })
    
    return render_template('event_search.html', events=events, keyword=keyword)

def get_weather(city_name):
    """OpenWeatherMapから天気情報を取得"""
    if not city_name:
        return "天気情報なし"
    
    params = {
        'q': city_name,
        'appid': WEATHER_API_KEY,
        'lang': 'ja',
        'units': 'metric'
    }
    try:
        res = requests.get(WEATHER_URL, params=params)
        if res.status_code == 200:
            data = res.json()
            weather = data['weather'][0]['description']
            temp = data['main']['temp']
            return f"{weather}（{temp}℃）"
        else:
            return "天気情報取得失敗"
    except:
        return "天気情報取得エラー"

if __name__ == '__main__':
    app.run(debug=True)



if __name__ == '__main__':
    # 開発用サーバーを実行
    app.run(debug=True)