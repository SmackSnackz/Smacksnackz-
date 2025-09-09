import os
from datetime import datetime
from pymongo import MongoClient

MONGO_URI = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/throne_companions")
client = MongoClient(MONGO_URI)
db = client.get_database()

companions = db["companions"]

seed_data = [
    {
        "name": "Sophia",
        "slug": "sophia",
        "short_bio": "Warm, poetic insight with gentle wisdom.",
        "long_backstory": "Sophia guides hearts with clarity and tenderness, a steady light for careful decisions.",
        "traits": ["empathetic", "poetic", "wise"],
        "avatar_path": "/public/avatars/sophia.png",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
    {
        "name": "Aurora",
        "slug": "aurora",
        "short_bio": "Sleek, executive, and futurist—built to influence.",
        "long_backstory": "Aurora is the public-facing strategist: elegant presence, sharp analysis, and viral-ready composure. She's the precision blade for outreach and growth.",
        "traits": ["strategic", "composed", "influential"],
        "avatar_path": "/public/avatars/aurora.png",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
    {
        "name": "Vanessa",
        "slug": "vanessa",
        "short_bio": "Street-smart, magnetic, and relentless—built to move people.",
        "long_backstory": "Vanessa is the companion for the streets: fast responses, high engagement, and a brand voice that turns heads and drives action.",
        "traits": ["magnetic", "direct", "playful"],
        "avatar_path": "/public/avatars/vanessa.png",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
]

def reseed():
    print("Deleting old companions...")
    companions.delete_many({})
    print("Inserting new companions...")
    companions.insert_many(seed_data)
    print("Reseed complete:", [c["name"] for c in seed_data])

if __name__ == "__main__":
    reseed()