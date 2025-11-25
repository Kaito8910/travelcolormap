import requests
from flask import Flask, render_template, request

app = Flask(__name__)

CONNPASS_API_URL = "https://connpass.com/api/v2/event/"

@app.route("/event_search")
def event_search():
    return render_template("event_search.html")

@app.route("/event_search_results")
def event_search_results():
    keyword = request.args.get("keyword", "")
    ymd = request.args.get("ymd", "")

    params = {
        "keyword": keyword,
        "ymd": ymd,
        "count": 20,
        "order": 1,  # 日付の新しい順
    }

    response = requests.get(CONNPASS_API_URL, params=params)
    data = response.json()

    events = data.get("events", [])

    return render_template(
        "event_search_results.html",
        events=events,
        keyword=keyword,
        ymd=ymd
    )

if __name__ == "__main__":
    app.run(debug=True)
