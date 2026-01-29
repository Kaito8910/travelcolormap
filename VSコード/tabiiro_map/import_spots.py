# import_spots.py
import json
from pathlib import Path

from app import app
from extensions import db
from models import Spots  # ★ class Spots を使う

JSON_PATH = Path("static/json/spots.json")

def import_spots(clear_before: bool = False):
    if not JSON_PATH.exists():
        raise FileNotFoundError(f"JSON not found: {JSON_PATH.resolve()}")

    with JSON_PATH.open(encoding="utf-8") as f:
        pref_list = json.load(f)

    with app.app_context():
        if clear_before:
            Spots.query.delete()
            db.session.commit()

        added = 0
        updated = 0
        skipped = 0

        for pref in pref_list:
            pref_code = pref.get("pref_code")                 # int
            pref_name_ja = pref.get("pref_name_ja", "")
            pref_name_en = pref.get("pref_name_en", "")
            region = pref.get("region", "")

            for s in pref.get("spots", []):
                spot_id = (s.get("spot_id") or "").strip()
                if not spot_id:
                    skipped += 1
                    continue

                spot = Spots.query.get(spot_id)
                if spot is None:
                    spot = Spots(spot_id=spot_id)
                    db.session.add(spot)
                    added += 1
                else:
                    updated += 1

                # JSON → DB
                spot.name = (s.get("spot_name") or "").strip()
                spot.city = (s.get("city") or "").strip()
                spot.category = (s.get("category") or "").strip()
                spot.description = (s.get("description") or "").strip()
                spot.image_url = (s.get("image_url") or "").strip()

                # pref情報（外側から）
                spot.pref_code = pref_code
                spot.pref_name_ja = pref_name_ja
                spot.pref_name_en = pref_name_en
                spot.region = region

        db.session.commit()
        print(f"✅ SPOTS import finished: added={added}, updated={updated}, skipped={skipped}")


if __name__ == "__main__":
    import_spots(clear_before=False)
