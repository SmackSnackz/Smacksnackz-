import os
from datetime import datetime
from pymongo import MongoClient, ASCENDING, DESCENDING

MONGO_URI = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/throne_companions")
client = MongoClient(MONGO_URI)
db = client.get_database()
companions = db["companions"]

# Indexes
companions.create_index([("slug", ASCENDING)], unique=True)
companions.create_index([("created_at", DESCENDING)])

seed = [
    {
        "name": "Sophia",
        "slug": "sophia",
        "short_bio": "Warm, poetic insight with gentle wisdom.",
        "long_backstory": "Sophia guides hearts with clarity and tenderness, a steady light for careful decisions.",
        "traits": ["empathetic", "poetic", "wise"],
        "avatar_path": "/avatars/sophia.png",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
    {
        "name": "Aurora",
        "slug": "aurora",
        "short_bio": "Sleek, executive, and futurist—built to influence.",
        "long_backstory": "Aurora is the public-facing strategist: elegant presence, sharp analysis, and viral-ready composure.",
        "traits": ["strategic", "composed", "influential"],
        "avatar_path": "/avatars/aurora.png",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
    {
        "name": "Vanessa",
        "slug": "vanessa",
        "short_bio": "Street-smart, magnetic, and relentless—built to move people.",
        "long_backstory": "Vanessa is built for high engagement and bold moves.",
        "traits": ["magnetic", "direct", "playful"],
        "avatar_path": "/avatars/vanessa.png",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
]

def run():
    print("Deleting old companions…")
    companions.delete_many({})
    print("Inserting new companions…")
    companions.insert_many(seed)
    print("Reseed complete:", [c["name"] for c in seed])

if __name__ == "__main__":
    run()