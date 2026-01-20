# utils/hotel_utils.py

import requests

APPLICATION_ID = "1002136947918553343"

def search_hotels(keyword, page=1, hits=20):
    url = "https://app.rakuten.co.jp/services/api/Travel/KeywordHotelSearch/20170426"
    params = {
        "applicationId": APPLICATION_ID,
        "format": "json",
        "keyword": keyword,
        "page": page,
        "hits": hits,
        "formatVersion": 2
    }
    resp = requests.get(url, params=params)
    data = resp.json()
    return data.get("hotels", [])


def extract_hotel_info(raw_hotels):
    hotels = []
    for wrapper in raw_hotels:
        if isinstance(wrapper, list) and len(wrapper) > 0:
            info = wrapper[0].get("hotelBasicInfo", {})
            hotels.append(info)
    return hotels
