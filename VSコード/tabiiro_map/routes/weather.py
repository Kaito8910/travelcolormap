# routes/weather.py

from flask import Blueprint, render_template, request, flash
from config import PREF_LATLON
from utils.weather_utils import convert_weather_icon
import requests

weather_bp = Blueprint("weather", __name__)


@weather_bp.route('/weather', methods=['GET', 'POST'])
def weather():
    weather_data = None
    weekly = None
    error = None

    if request.method == "POST":
        pref = request.form.get("prefecture")

        if pref not in PREF_LATLON:
            error = "都道府県を選択してください。"
        else:
            lat, lon = PREF_LATLON[pref]

            url = (
                "https://api.open-meteo.com/v1/forecast"
                f"?latitude={lat}&longitude={lon}"
                "&current_weather=true"
                "&daily=weathercode,temperature_2m_max,temperature_2m_min,precipitation_probability_max"
                "&timezone=Asia/Tokyo"
            )

            try:
                res = requests.get(url).json()

                code = res["current_weather"]["weathercode"]

                weather_data = {
                    "city_name": pref,
                    "description": "現在の天気",
                    "temp": res["current_weather"]["temperature"],
                    "humidity": "-",
                    "icon": convert_weather_icon(code),
                }

                weekly = []
                for i in range(7):
                    w_code = res["daily"]["weathercode"][i]
                    weekly.append({
                        "date": res["daily"]["time"][i],
                        "icon": convert_weather_icon(w_code),
                        "max": res["daily"]["temperature_2m_max"][i],
                        "min": res["daily"]["temperature_2m_min"][i],
                        "precip": res["daily"]["precipitation_probability_max"][i],
                    })

            except Exception:
                error = "天気データの取得に失敗しました。"

    return render_template(
        "weather.html",
        weather=weather_data,
        weekly=weekly,
        error=error,
        prefectures=list(PREF_LATLON.keys())
    )
