from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from bson import ObjectId
from db import db
from routers import tts_router  # your TTS router
from routers import routes_nearby as places_router
# ---------------------
# Initialize App
# ---------------------
app = FastAPI()
app.include_router(tts_router.router)
app.include_router(places_router)
# Allow all origins (Flutter/mobile)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------
# Pydantic Models
# ---------------------
class PostIn(BaseModel):
    # GeoJSON Point
    location: Dict[str, Any] = Field(
        ..., example={"type": "Point", "coordinates": [76.89805, 8.51568]}
    )
    description_brief: str
    description_detail: str


class PostOut(PostIn):
    id: str = Field(default_factory=str)


# ---------------------
# Routes
# ---------------------
@app.get("/")
def read_root():
    return {"message": "Blogger API is running with GeoJSON!"}


# Create Post
@app.post("/posts", response_model=PostOut)
async def create_post(post: PostIn):
    result = await db.posts.insert_one(post.dict())
    created = await db.posts.find_one({"_id": result.inserted_id})
    return {**created, "id": str(created["_id"])}


# Get All Posts
@app.get("/posts", response_model=List[PostOut])
async def get_posts():
    posts = await db.posts.find().to_list(100)
    return [{**p, "id": str(p["_id"])} for p in posts]


# Get Single Post by ID
@app.get("/posts/{post_id}", response_model=PostOut)
async def get_post(post_id: str):
    post = await db.posts.find_one({"_id": ObjectId(post_id)})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return {**post, "id": str(post["_id"])}


# Update Post
@app.put("/posts/{post_id}", response_model=PostOut)
async def update_post(post_id: str, post: PostIn):
    result = await db.posts.update_one(
        {"_id": ObjectId(post_id)}, {"$set": post.dict()}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Post not found")
    updated = await db.posts.find_one({"_id": ObjectId(post_id)})
    return {**updated, "id": str(updated["_id"])}


# Delete Post
@app.delete("/posts/{post_id}")
async def delete_post(post_id: str):
    result = await db.posts.delete_one({"_id": ObjectId(post_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"message": "Post deleted successfully"}


# ---------------------
# Nearby Search (500m by default)
# ---------------------
@app.get("/posts/nearby", response_model=List[PostOut])
async def get_nearby_posts(
    lat: float = Query(...),
    lng: float = Query(...),
    radius: int = Query(500, description="Search radius in meters")
):
    query = {
        "location": {
            "$near": {
                "$geometry": {"type": "Point", "coordinates": [lng, lat]},
                "$maxDistance": radius,
            }
        }
    }

    posts = []
    async for doc in db.posts.find(query):
        posts.append({**doc, "id": str(doc["_id"])})
    return posts
