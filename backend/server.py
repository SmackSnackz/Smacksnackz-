from fastapi import FastAPI, APIRouter, HTTPException, Query
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

class Companion(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    short_bio: str
    long_backstory: str
    traits: List[str]
    avatar_path: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CompanionCreate(BaseModel):
    name: str
    short_bio: str
    long_backstory: str
    traits: List[str]
    avatar_path: str = "/assets/companion-default.png"

class CompanionUpdate(BaseModel):
    name: Optional[str] = None
    short_bio: Optional[str] = None
    long_backstory: Optional[str] = None
    traits: Optional[List[str]] = None
    avatar_path: Optional[str] = None

class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    companion_id: str
    session_id: str  # guest_session_id for guest users
    message: str
    is_user: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ChatRequest(BaseModel):
    companion_id: str
    message: str
    session_id: str

class ChatResponse(BaseModel):
    id: str
    companion_id: str
    session_id: str
    message: str
    is_user: bool
    timestamp: datetime

# Initialize database indexes
async def init_db():
    """Initialize database collections and indexes"""
    try:
        # Create indexes for companions
        await db.companions.create_index("id", unique=True)
        await db.companions.create_index("name")
        
        # Create indexes for chat messages
        await db.chat_messages.create_index("id", unique=True)
        await db.chat_messages.create_index([("companion_id", 1), ("session_id", 1)])
        await db.chat_messages.create_index("timestamp")
        
        # Create indexes for status checks
        await db.status_checks.create_index("id", unique=True)
        
        logging.info("Database indexes created successfully")
    except Exception as e:
        logging.error(f"Error creating database indexes: {e}")

# Seed data
async def seed_companions():
    """Seed initial companion data"""
    try:
        # Check if companions already exist
        existing_count = await db.companions.count_documents({})
        if existing_count > 0:
            logging.info("Companions already seeded")
            return
        
        companions_data = [
            {
                "id": str(uuid.uuid4()),
                "name": "Sophia",
                "short_bio": "Wise and thoughtful, provides deep insights about life and philosophy.",
                "long_backstory": "Sophia is an ancient soul who has observed the patterns of human existence for millennia. She speaks with the wisdom of ages, offering profound insights into the nature of consciousness, love, and the meaning of life. Her gentle demeanor masks a sharp intellect that can unravel the most complex philosophical questions. She finds joy in helping others discover their own inner wisdom and potential.",
                "traits": ["Wise", "Philosophical", "Empathetic", "Patient", "Insightful"],
                "avatar_path": "/assets/sophia-avatar.png",
                "created_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Nova",
                "short_bio": "Energetic and creative, loves exploring new ideas and innovative solutions.",
                "long_backstory": "Nova embodies the spirit of innovation and boundless creativity. She approaches every challenge with infectious enthusiasm and an unshakeable belief that there's always a better way to do things. Her mind works at lightning speed, connecting disparate ideas into brilliant solutions. She thrives on brainstorming sessions, creative projects, and helping others break through mental barriers to achieve their wildest dreams.",
                "traits": ["Creative", "Energetic", "Innovative", "Optimistic", "Inspiring"],
                "avatar_path": "/assets/nova-avatar.png",
                "created_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Zara",
                "short_bio": "Empathetic and caring, always there to listen and offer comfort.",
                "long_backstory": "Zara possesses an extraordinary gift for emotional intelligence and genuine empathy. She has an innate ability to understand what others are feeling, often before they understand it themselves. Her presence brings immediate comfort to those in distress, and her words have a healing quality that soothes troubled hearts. She believes deeply in the power of human connection and the importance of being truly heard and understood.",
                "traits": ["Empathetic", "Caring", "Supportive", "Intuitive", "Compassionate"],
                "avatar_path": "/assets/zara-avatar.png",
                "created_at": datetime.utcnow()
            }
        ]
        
        result = await db.companions.insert_many(companions_data)
        logging.info(f"Seeded {len(result.inserted_ids)} companions successfully")
        
    except Exception as e:
        logging.error(f"Error seeding companions: {e}")

# Basic status endpoints
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# Companion endpoints
@api_router.get("/companions", response_model=List[Companion])
async def get_companions():
    """Get all companions"""
    try:
        companions = await db.companions.find().to_list(1000)
        return [Companion(**companion) for companion in companions]
    except Exception as e:
        logging.error(f"Error getting companions: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve companions")

@api_router.post("/companions", response_model=Companion)
async def create_companion(companion_data: CompanionCreate):
    """Create a new companion"""
    try:
        companion = Companion(**companion_data.dict())
        await db.companions.insert_one(companion.dict())
        return companion
    except Exception as e:
        logging.error(f"Error creating companion: {e}")
        raise HTTPException(status_code=500, detail="Failed to create companion")

@api_router.get("/companions/{companion_id}", response_model=Companion)
async def get_companion(companion_id: str):
    """Get a specific companion by ID"""
    try:
        companion = await db.companions.find_one({"id": companion_id})
        if not companion:
            raise HTTPException(status_code=404, detail="Companion not found")
        return Companion(**companion)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting companion {companion_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve companion")

@api_router.put("/companions/{companion_id}", response_model=Companion)
async def update_companion(companion_id: str, update_data: CompanionUpdate):
    """Update a companion"""
    try:
        # Check if companion exists
        existing = await db.companions.find_one({"id": companion_id})
        if not existing:
            raise HTTPException(status_code=404, detail="Companion not found")
        
        # Update with only provided fields
        update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
        if update_dict:
            await db.companions.update_one({"id": companion_id}, {"$set": update_dict})
        
        # Return updated companion
        updated_companion = await db.companions.find_one({"id": companion_id})
        return Companion(**updated_companion)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error updating companion {companion_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update companion")

@api_router.delete("/companions/{companion_id}")
async def delete_companion(companion_id: str):
    """Delete a companion"""
    try:
        result = await db.companions.delete_one({"id": companion_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Companion not found")
        
        # Also delete associated chat messages
        await db.chat_messages.delete_many({"companion_id": companion_id})
        
        return {"message": "Companion deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error deleting companion {companion_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete companion")

# Chat endpoints
@api_router.post("/chat", response_model=ChatResponse)
async def chat_with_companion(chat_request: ChatRequest):
    """Send a message to a companion and get a response"""
    try:
        # Verify companion exists
        companion = await db.companions.find_one({"id": chat_request.companion_id})
        if not companion:
            raise HTTPException(status_code=404, detail="Companion not found")
        
        # Store user message
        user_message = ChatMessage(
            companion_id=chat_request.companion_id,
            session_id=chat_request.session_id,
            message=chat_request.message,
            is_user=True
        )
        await db.chat_messages.insert_one(user_message.dict())
        
        # Generate companion response (simple echo for now - can be enhanced with AI)
        companion_response_text = f"Hello! I'm {companion['name']}. {companion['short_bio']} You said: '{chat_request.message}'. How can I help you today?"
        
        companion_message = ChatMessage(
            companion_id=chat_request.companion_id,
            session_id=chat_request.session_id,
            message=companion_response_text,
            is_user=False
        )
        await db.chat_messages.insert_one(companion_message.dict())
        
        return ChatResponse(**companion_message.dict())
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail="Failed to process chat message")

@api_router.get("/chat/{companion_id}")
async def get_chat_history(companion_id: str, session_id: str = Query(...)):
    """Get chat history for a companion and session"""
    try:
        messages = await db.chat_messages.find({
            "companion_id": companion_id,
            "session_id": session_id
        }).sort("timestamp", 1).to_list(1000)
        
        return [ChatResponse(**message) for message in messages]
    except Exception as e:
        logging.error(f"Error getting chat history: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve chat history")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    await init_db()
    await seed_companions()

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()