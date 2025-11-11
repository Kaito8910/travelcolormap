from flask import Flask, render_template, jsonify, request, abort

app = Flask(__name__)

# === APIキー設定 ===
JARAN_API_KEY = "7e7c8f15291d905e"
WEATHER_API_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
JARAN_URL = "https://webservice.recruit.co.jp/ab-event/v1/"
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"



@app.route('/')
def home():
    return render_template('home.html')

@app.route('/user-data', endpoint='user_data', methods=['GET'])
def user_data():
    try:
        return render_template('accounts/user_data.html', user=None)
    except Exception:
        return "<h1>アカウント情報ページ</h1>"


# 地図の色付けデータを提供するAPIエンドポイント
@app.route('/api/travel-records')
def travel_records_api():
    # ⚠️ 注意: ここにデータベースからデータを取得するロジックを実装してください.
    
    # 仮のデータ (都道府県ID 'prefXX' とステータス)
    data = {
        'pref13': {'status': 'visited', 'count': 5},    # 東京都
        'pref27': {'status': 'want_to_go', 'count': 2}, # 大阪府
        'pref40': {'status': 'visited', 'count': 8},    # 福岡県
        'pref01': {'status': 'visited', 'count': 1},    # 北海道
        'pref22': {'status': 'want_to_go', 'count': 3}  # 静岡県
    }
    return jsonify(data)



@app.route('/event-search', methods=['GET', 'POST'])
def event_search():
    if request.method == 'GET':
        return render_template('event_search.html', events=None)

    keyword = request.form.get('keyword', '')
    area = request.form.get('area', '')
    date = request.form.get('date', '')
    category = request.form.get('category', '')

    params = {
        'key': JARAN_API_KEY,
        'keyword': f"{area} {keyword} {category}",
        'format': 'json',
        'count': 10
    }

    events = []
    try:
        resp = request.get(JARAN_URL, params=params, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            results = data.get('results', {}).get('event', [])
            for e in results:
                start = e.get('event_start_date', '')
                end = e.get('event_end_date', '')
                if date and not (start <= date <= end):
                    continue

                events.append({
                    'name': e.get('event_name', '不明なイベント'),
                    'period': f"{start} ～ {end}",
                    'location': e.get('event_place', ''),
                    'summary': (e.get('event_caption', '')[:100] + "...") if e.get('event_caption') else '',
                    'weather': get_weather(e.get('event_place', ''))
                })
    except Exception as e:
        print("Error:", e)
        events = []

    return render_template(
        'event_search.html',
        events=events,
        keyword=keyword,
        area=area,
        date=date,
        category=category
    )





if __name__ == '__main__':
    # 開発用サーバーを実行
    app.run(debug=True)