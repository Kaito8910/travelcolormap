import json
import os
from config import Config

def load_spots_json():
    path = Config.SPOTS_JSON_PATH
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_events_json():
    path = Config.EVENTS_JSON_PATH
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_prefecture_list():
    data = load_spots_json()
    return [p["pref_name_ja"] for p in data]
