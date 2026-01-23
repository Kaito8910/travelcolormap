from app import app, db
from models import Spot
import json

with app.app_context():
    with open("static/json/spots.json", encoding="utf-8") as f:
        data = json.load(f)

    for pref in data:
        for s in pref["spots"]:
            #  skip if already exists
            if Spot.query.get(s["spot_id"]):
                continue

            spot = Spot(
                spot_id=s["spot_id"],
                name=s["spot_name"],
                city=s["city"],
                category=s["category"],
                description=s["description"],
                image_url=s["image_url"],
                pref_code=pref["pref_code"],
                pref_name_ja=pref["pref_name_ja"],
                pref_name_en=pref["pref_name_en"],
                region=pref["region"]
            )
            db.session.add(spot)

    db.session.commit()
    print("✅ spots imported successfully")
