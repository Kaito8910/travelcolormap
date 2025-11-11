from flask import Flask, render_template, jsonify, request, abort
import requests

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


#------------------------ イベント検索機能 -----------------------------------

# --- イベント検索フォーム ---
@app.route('/event-search', methods=['GET'])
def event_search():
    return render_template('event_search.html')


# --- 検索結果 ---
@app.route('/event-search-results', methods=['POST'])
def event_search_results():
    # フォームから値を取得
    area = request.form.get('area', '')
    category = request.form.get('category', '')
    date = request.form.get('date', '')

    print("受け取った検索条件:", area, category, date)  # デバッグ用

    # API用キーワード生成（キーワード欄はなし）
    keyword_list = [area, category]
    api_keyword = " ".join(filter(None, keyword_list))
    params = {
        'key': JARAN_API_KEY,
        'keyword': api_keyword,
        'format': 'json',
        'count': 5
    }

    print("APIに送るパラメータ:", params)  # デバッグ用

    events = []
    try:
        resp = requests.get(JARAN_URL, params=params, timeout=5)
        print("APIステータスコード:", resp.status_code)  # デバッグ用

        if resp.status_code == 200:
            data = resp.json()
            results = data.get('results', {}).get('event', [])
            print("取得件数:", len(results))  # デバッグ用

            for e in results:
                name = e.get('event_name', '不明なイベント')
                start_date = e.get('event_start_date', '')
                end_date = e.get('event_end_date', '')
                location = e.get('event_place', '')
                summary = (e.get('event_caption', '')[:100] + "...") if e.get('event_caption') else ''
                events.append({
                    'name': name,
                    'period': f"{start_date} ～ {end_date}",
                    'location': location,
                    'summary': summary
                })
    except Exception as ex:
        print("イベント取得エラー:", ex)
        events = []

    return render_template(
        'event_search_results.html',
        events=events,
        area=area,
        category=category,
        date=date
    )


#---------------------------------------------------------------------------


if __name__ == '__main__':
    # 開発用サーバーを実行
    app.run(debug=True)