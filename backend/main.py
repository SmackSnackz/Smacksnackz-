import os
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient, ASCENDING, DESCENDING
from bson import ObjectId

MONGO_URI = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/throne_companions")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "CHANGE_ME")

client = MongoClient(MONGO_URI)
db = client.get_database()
companions = db["companions"]
messages = db["messages"]

# Indexes
companions.create_index([("slug", ASCENDING)], unique=True)
companions.create_index([("created_at", DESCENDING)])
messages.create_index([("session_id", ASCENDING), ("created_at", DESCENDING)])
messages.create_index([("companion_id", ASCENDING)])

def oid(s: str) -> ObjectId:
    try:
        return ObjectId(s)
    except Exception:
        raise HTTPException(status_code=400, detail="invalid_id")

def to_dict(doc):
    doc["_id"] = str(doc["_id"])
    return doc

def admin_guard(req: Request):
    auth = req.headers.get("authorization", "")
    token = auth.replace("Bearer ", "")
    if not ADMIN_TOKEN or token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="unauthorized")

class CompanionIn(BaseModel):
    name: str
    slug: str
    short_bio: str
    long_backstory: Optional[str] = ""
    traits: List[str] = []
    avatar_path: Optional[str] = "/public/assets/logo.png"

class ChatIn(BaseModel):
    companion_id: str
    message: str
    session_id: str

app = FastAPI()

# CORS (adjust origin to your production domain when ready)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten to your domain later
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health():
    return {"ok": True, "time": datetime.utcnow().isoformat()}

# -------- Companions --------
@app.get("/api/companions")
def list_companions():
    docs = list(companions.find({}, {"name":1,"slug":1,"short_bio":1,"avatar_path":1}).sort("created_at", DESCENDING))
    return [to_dict(d) for d in docs]

@app.post("/api/companions")
def create_companion(payload: CompanionIn, _: None = Depends(admin_guard)):
    if companions.find_one({"slug": payload.slug}):
        raise HTTPException(status_code=409, detail="slug_exists")
    now = datetime.utcnow()
    doc = {**payload.dict(), "created_at": now, "updated_at": now}
    res = companions.insert_one(doc)
    return to_dict(companions.find_one({"_id": res.inserted_id}))

@app.get("/api/companions/{companion_id}")
def get_companion(companion_id: str):
    doc = companions.find_one({"_id": oid(companion_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="not_found")
    return to_dict(doc)

@app.put("/api/companions/{companion_id}")
def update_companion(companion_id: str, payload: CompanionIn, _: None = Depends(admin_guard)):
    now = datetime.utcnow()
    res = companions.find_one_and_update(
        {"_id": oid(companion_id)},
        {"$set": {**payload.dict(), "updated_at": now}},
        return_document=True,
    )
    if not res:
        raise HTTPException(status_code=404, detail="not_found")
    return to_dict(res)

@app.delete("/api/companions/{companion_id}")
def delete_companion(companion_id: str, _: None = Depends(admin_guard)):
    res = companions.find_one_and_delete({"_id": oid(companion_id)})
    if not res:
        raise HTTPException(status_code=404, detail="not_found")
    return {"ok": True}

# -------- Chat --------
def persona_reply(comp: dict, text: str) -> str:
    traits = ", ".join(comp.get("traits", []))
    bio = comp.get("short_bio", "")
    last = text.strip()
    return f"{comp['name']}: {bio} ({traits})\n→ {last}\nAsk me anything; I'm here."

@app.post("/api/chat")
def post_chat(body: ChatIn):
    comp = companions.find_one({"_id": oid(body.companion_id)})
    if not comp:
        raise HTTPException(status_code=404, detail="companion_not_found")
    now = datetime.utcnow()
    # store user msg
    messages.insert_one({
        "companion_id": comp["_id"],
        "session_id": body.session_id,
        "role": "user",
        "content": body.message,
        "created_at": now
    })
    # reply
    reply_text = persona_reply(comp, body.message)
    messages.insert_one({
        "companion_id": comp["_id"],
        "session_id": body.session_id,
        "role": "assistant",
        "content": reply_text,
        "created_at": datetime.utcnow()
    })
    # return recent thread
    thread = list(messages.find(
        {"companion_id": comp["_id"], "session_id": body.session_id}
    ).sort("created_at", ASCENDING).limit(50))
    for m in thread:
        m["_id"] = str(m["_id"])
        m["companion_id"] = str(m["companion_id"])
    return {"reply": reply_text, "thread": thread}