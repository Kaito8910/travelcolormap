# import_events.py
import json
from pathlib import Path

from app import app
from extensions import db
from models import Event

# ★ JSONの場所（ここ重要）
JSON_PATH = Path("static/json/events.json")

def import_events(clear_before=False):
    if not JSON_PATH.exists():
        raise FileNotFoundError(f"JSON not found: {JSON_PATH.resolve()}")

    with JSON_PATH.open(encoding="utf-8") as f:
        pref_list = json.load(f)

    with app.app_context():
        if clear_before:
            Event.query.delete()
            db.session.commit()

        added = 0
        updated = 0

        for pref in pref_list:
            pref_code = str(pref.get("pref_code"))
            pref_name = pref.get("pref_name_ja")

            for e in pref.get("events", []):
                event_code = e.get("event_id")
                if not event_code:
                    continue

                event = Event.query.get(event_code)
                if event is None:
                    event = Event(event_code=event_code)
                    db.session.add(event)
                    added += 1
                else:
                    updated += 1

                event.title = e.get("event_name")
                event.category = e.get("category")
                event.description = e.get("description")
                event.month = e.get("month")      # "2月上旬"
                event.city = e.get("city")
                event.url = e.get("event_url")
                event.image_url = e.get("image_url")
                event.pref_code = pref_code
                event.pref_name = pref_name

        db.session.commit()
        print(f"✅ import finished: added={added}, updated={updated}")


if __name__ == "__main__":
    import_events(clear_before=False)
