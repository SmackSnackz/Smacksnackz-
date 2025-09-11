import os
from datetime import datetime
from pymongo import MongoClient, ASCENDING, DESCENDING
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://127.0.0.1:27017")
DB_NAME = os.getenv("DB_NAME", "test_database")

client = MongoClient(MONGO_URL)
db = client[DB_NAME]
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
        "avatar_path": "/public/avatars/sophia.png",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
    {
        "name": "Aurora",
        "slug": "aurora",
        "short_bio": "Sleek, executive, and futurist—built to influence.",
        "long_backstory": "Aurora is the public-facing strategist: elegant presence, sharp analysis, and viral-ready composure.",
        "traits": ["strategic", "composed", "influential"],
        "avatar_path": "/public/avatars/aurora.png",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
    {
        "name": "Vanessa",
        "slug": "vanessa",
        "short_bio": "Street-smart, magnetic, and relentless—built to move people.",
        "long_backstory": "Vanessa is built for high engagement and bold moves.",
        "traits": ["magnetic", "direct", "playful"],
        "avatar_path": "/public/avatars/vanessa.png",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
    {
        "name": "Selene",
        "slug": "selene",
        "short_bio": "Mystical and untamed, a gypsy spirit with cosmic fire.",
        "long_backstory": "Selene embodies mystery and allure: beads, silks, moonlight, and the secrets of the unseen world.",
        "traits": ["mystical", "confident", "enchanting"],
        "avatar_path": "/public/avatars/selene.png",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
    {
        "name": "Cassian",
        "slug": "cassian",
        "short_bio": "Calm, strategic, with a protective edge.",
        "long_backstory": "Raised in chaos, disciplined through sports and life lessons, Cassian reads the room and moves like a tactician.",
        "traits": ["protective", "strategic", "grounded"],
        "avatar_path": "/public/avatars/cassian.png",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
    {
        "name": "Lysander",
        "slug": "lysander",
        "short_bio": "Brilliant tactician, slender and dreamy intellect.",
        "long_backstory": "Lysander is the nerd-hero: sharp mind, soft presence, slender but magnetic, always seeing ten moves ahead.",
        "traits": ["intellectual", "dreamy", "tactician"],
        "avatar_path": "/public/avatars/lysander.png",
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