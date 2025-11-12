from flask import Flask, render_template, jsonify, session, redirect, url_for, request, abort
import requests, request, abort
import requests

app = Flask(__name__)

# === APIキー設定 ===
JARAN_API_KEY = "7e7c8f15291d905e"
WEATHER_API_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
JARAN_URL = "https://webservice.recruit.co.jp/ab-event/v1/"
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"



# ホーム画面 (日本地図表示)
app.secret_key = 'your_secret_key'  # セッション管理に必須（本番では安全な値を設定）

# === APIキー設定 ===
JARAN_API_KEY = "7e7c8f15291d905e"
WEATHER_API_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
JARAN_URL = "https://webservice.recruit.co.jp/ab-event/v1/"
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"


# ===============================================================
# 🏠 ホーム画面（日本地図表示）
# ===============================================================
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/user-data', endpoint='user_data', methods=['GET'])
def user_data():
    try:
        return render_template('accounts/user_data.html', user=None)
    except Exception:
        return "<h1>アカウント情報ページ</h1>"


# ===============================================================
# 👤 ログイン・ログアウト・アカウント管理
# ===============================================================

# --- ログイン ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # 簡易的な認証例
        if username == 'user' and password == 'pass':
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('home'))
        else:
            return "<h3>ログイン失敗しました。ユーザー名かパスワードが違います。</h3>"

    return '''
        <form method="post">
            <input type="text" name="username" placeholder="ユーザー名"><br>
            <input type="password" name="password" placeholder="パスワード"><br>
            <button type="submit">ログイン</button>
        </form>
    '''


# --- ログアウト ---
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('home'))


# --- アカウント情報ページ ---
@app.route('/user-data')
def user_data():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    username = session.get('username', 'ゲスト')
    return f"<h1>{username} さんのアカウント情報ページ</h1>"


# ===============================================================
# 📖 各種ページ
# ===============================================================

@app.route('/travel-record')
def travel_record():
    return "<h1>旅行先記録ページ</h1>"

@app.route('/gourmet-record')
def gourmet_record():
    return "<h1>グルメ記録ページ</h1>"

@app.route('/stay-search')
def stay_search():
    return "<h1>宿泊検索ページ</h1>"

@app.route('/event-search')
def event_search():
    return render_template('event_search.html')


# ===============================================================
# 🗾 日本地図データ API
# ===============================================================
@app.route('/api/travel-records')
def travel_records_api():
    # 仮のデータ (Japan Mapが期待する形式: ID 'prefXX' とステータス)
    data = {
        'pref13': {'status': 'visited', 'count': 5},    # 東京
        'pref27': {'status': 'want_to_go', 'count': 2}, # 大阪
        'pref40': {'status': 'visited', 'count': 8},    # 福岡
        'pref01': {'status': 'visited', 'count': 1},    # 北海道
        'pref22': {'status': 'want_to_go', 'count': 3}  # 静岡
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



# ===============================================================
# 🎉 イベント検索機能 (じゃらんAPI)
# ===============================================================
@app.route('/event-search-results', methods=['POST'])
def event_search_results():
    # フォームから値を取得
    area = request.form.get('area', '')
    category = request.form.get('category', '')
    date = request.form.get('date', '')

    print("受け取った検索条件:", area, category, date)

    keyword_list = [area, category]
    api_keyword = " ".join(filter(None, keyword_list))
    params = {
        'key': JARAN_API_KEY,
        'keyword': api_keyword,
        'format': 'json',
        'count': 5
    }

    print("APIに送るパラメータ:", params)

    events = []
    try:
        resp = requests.get(JARAN_URL, params=params, timeout=5)
        print("APIステータスコード:", resp.status_code)

        if resp.status_code == 200:
            data = resp.json()
            results = data.get('results', {}).get('event', [])
            print("取得件数:", len(results))

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


# ===============================================================
# 🧭 アプリ起動
# ===============================================================
if __name__ == '__main__':
    app.run(debug=True)



