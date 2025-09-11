from fastapi import FastAPI, APIRouter, HTTPException
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


# Define Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

class Companion(BaseModel):
    name: str
    slug: str
    short_bio: str
    long_backstory: str
    traits: List[str]
    avatar_path: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class CompanionCreate(BaseModel):
    name: str
    slug: str
    short_bio: str
    long_backstory: str
    traits: List[str]
    avatar_path: str

class CompanionUpdate(BaseModel):
    name: Optional[str] = None
    short_bio: Optional[str] = None
    long_backstory: Optional[str] = None
    traits: Optional[List[str]] = None
    avatar_path: Optional[str] = None

class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    companion_slug: str
    user_message: str
    companion_response: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ChatRequest(BaseModel):
    message: str

# Add your routes to the router instead of directly to app
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

# Companions endpoints
@api_router.get("/companions", response_model=List[Companion])
async def get_companions():
    companions = await db.companions.find().to_list(1000)
    return [Companion(**companion) for companion in companions]

@api_router.get("/companions/{slug}", response_model=Companion)
async def get_companion(slug: str):
    companion = await db.companions.find_one({"slug": slug})
    if not companion:
        raise HTTPException(status_code=404, detail="Companion not found")
    return Companion(**companion)

@api_router.post("/companions", response_model=Companion)
async def create_companion(companion_data: CompanionCreate):
    # Check if slug already exists
    existing = await db.companions.find_one({"slug": companion_data.slug})
    if existing:
        raise HTTPException(status_code=400, detail="Companion with this slug already exists")
    
    companion_dict = companion_data.dict()
    companion_obj = Companion(**companion_dict)
    await db.companions.insert_one(companion_obj.dict())
    return companion_obj

@api_router.put("/companions/{slug}", response_model=Companion)
async def update_companion(slug: str, companion_data: CompanionUpdate):
    companion = await db.companions.find_one({"slug": slug})
    if not companion:
        raise HTTPException(status_code=404, detail="Companion not found")
    
    update_data = {k: v for k, v in companion_data.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    await db.companions.update_one({"slug": slug}, {"$set": update_data})
    updated_companion = await db.companions.find_one({"slug": slug})
    return Companion(**updated_companion)

@api_router.delete("/companions/{slug}")
async def delete_companion(slug: str):
    result = await db.companions.delete_one({"slug": slug})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Companion not found")
    return {"message": "Companion deleted successfully"}

# Chat endpoint
@api_router.post("/chat/{companion_slug}", response_model=ChatMessage)
async def chat_with_companion(companion_slug: str, chat_request: ChatRequest):
    # Check if companion exists
    companion = await db.companions.find_one({"slug": companion_slug})
    if not companion:
        raise HTTPException(status_code=404, detail="Companion not found")
    
    # Simple response based on companion's traits and personality
    companion_data = Companion(**companion)
    
    # Generate a simple response based on the companion's personality
    responses = {
        "sophia": f"*Speaking with gentle wisdom* {chat_request.message} - I understand your thoughts. Let me share some poetic insight that might help guide you with clarity and tenderness.",
        "aurora": f"*With executive composure* {chat_request.message} - I've analyzed your message strategically. Here's my sleek, influential perspective on moving forward.",
        "vanessa": f"*With magnetic energy* {chat_request.message} - That's interesting! Let me give you my direct, street-smart take on this. I'm built to move people to action."
    }
    
    default_response = f"*As {companion_data.name}* {chat_request.message} - Thank you for sharing that with me. Based on my traits of being {', '.join(companion_data.traits)}, here's my perspective."
    
    companion_response = responses.get(companion_slug, default_response)
    
    chat_message = ChatMessage(
        companion_slug=companion_slug,
        user_message=chat_request.message,
        companion_response=companion_response
    )
    
    await db.chat_messages.insert_one(chat_message.dict())
    return chat_message

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

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
