from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from db import db
from bson import ObjectId

app = FastAPI()

# Allow all origins (for Flutter)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# Pydantic Models
# ----------------------------
class Trip(BaseModel):
    destination: str
    date: str

class TripResponse(Trip):
    id: str

class Post(BaseModel):
    latitude: float = Field(..., example=10.12345)
    longitude: float = Field(..., example=76.54321)
    description_brief: str = Field(..., example="Beautiful tea plantations")
    description_detail: str = Field(..., example="This place is known for its scenic tea gardens in Munnar...")

class PostResponse(Post):
    id: str

# ----------------------------
# Helpers
# ----------------------------
def serialize_doc(doc):
    """Convert MongoDB document to JSON-serializable dict"""
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc

# ----------------------------
# Routes
# ----------------------------
@app.get("/")
def read_root():
    return {"message": "Blogger API is running!"}

# ---- Trips API ----
@app.post("/trips", response_model=TripResponse)
async def add_trip(trip: Trip):
    result = await db.trips.insert_one(trip.dict())
    return {"id": str(result.inserted_id), **trip.dict()}

@app.get("/trips", response_model=List[TripResponse])
async def get_trips():
    trips = await db.trips.find().to_list(100)
    return [serialize_doc(t) for t in trips]

@app.put("/trips/{trip_id}", response_model=TripResponse)
async def update_trip(trip_id: str, trip: Trip):
    result = await db.trips.update_one({"_id": ObjectId(trip_id)}, {"$set": trip.dict()})
    if result.matched_count == 0:
        raise HTTPException(404, "Trip not found")
    updated = await db.trips.find_one({"_id": ObjectId(trip_id)})
    return serialize_doc(updated)

@app.delete("/trips/{trip_id}")
async def delete_trip(trip_id: str):
    result = await db.trips.delete_one({"_id": ObjectId(trip_id)})
    if result.deleted_count == 0:
        raise HTTPException(404, "Trip not found")
    return {"message": "Trip deleted"}

# ---- Posts API ----
@app.post("/posts", response_model=PostResponse)
async def create_post(post: Post):
    result = await db.posts.insert_one(post.dict())
    return {"id": str(result.inserted_id), **post.dict()}

@app.get("/posts", response_model=List[PostResponse])
async def get_posts():
    posts = await db.posts.find().to_list(100)
    return [serialize_doc(p) for p in posts]

@app.get("/posts/{post_id}", response_model=PostResponse)
async def get_post(post_id: str):
    post = await db.posts.find_one({"_id": ObjectId(post_id)})
    if not post:
        raise HTTPException(404, "Post not found")
    return serialize_doc(post)

@app.put("/posts/{post_id}", response_model=PostResponse)
async def update_post(post_id: str, post: Post):
    result = await db.posts.update_one({"_id": ObjectId(post_id)}, {"$set": post.dict()})
    if result.matched_count == 0:
        raise HTTPException(404, "Post not found")
    updated = await db.posts.find_one({"_id": ObjectId(post_id)})
    return serialize_doc(updated)

@app.delete("/posts/{post_id}")
async def delete_post(post_id: str):
    result = await db.posts.delete_one({"_id": ObjectId(post_id)})
    if result.deleted_count == 0:
        raise HTTPException(404, "Post not found")
    return {"message": "Post deleted"}
