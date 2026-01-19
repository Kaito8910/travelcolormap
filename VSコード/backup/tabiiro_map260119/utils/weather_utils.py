# utils/weather_utils.py

def convert_weather_icon(code):
    if code == 0: return "☀️"
    if code == 1: return "🌤"
    if code == 2: return "⛅"
    if code == 3: return "☁️"
    if code in [45, 48]: return "🌫"
    if code in [51, 53, 55]: return "🌧"
    if code in [61, 63, 65]: return "🌧"
    if code in [66, 67]: return "🌧❄️"
    if code in [71, 73, 75]: return "❄️"
    if code == 77: return "🌨"
    if code in [80, 81, 82]: return "🌦"
    if code in [85, 86]: return "🌨"
    if code == 95: return "⛈️"
    if code in [96, 99]: return "⛈️"
    return "❓"
