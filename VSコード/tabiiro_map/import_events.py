import json
from app import create_app
from models import db, Event

app = create_app()

with app.app_context():
    with open("static/json/events.json", encoding="utf-8") as f:
        data = json.load(f)

    for pref in data:
        pref_code = pref["pref_code"]
        pref_name = pref["pref_name_ja"]

        for e in pref["events"]:
            event = Event(
                title=e["event_name"],         
                city=e["city"],
                month=e["month"],
                category=e["category"],
                description=e["description"],
                url=e["event_url"],
                pref_code=pref_code,
                pref_name=pref_name
            )
            db.session.add(event)

    db.session.commit()
    print("✅ Events imported successfully")
