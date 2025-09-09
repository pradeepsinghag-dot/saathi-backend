from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List
from bson import ObjectId
from db import db
from routers import tts_router  # import your TTS router

# Initialize FastAPI app first
app = FastAPI()

# Include the TTS router AFTER app is created
app.include_router(tts_router.router)

# Allow all origins (for Flutter or mobile app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------
# Pydantic Models
# ---------------------
class Post(BaseModel):
    latitude: float
    longitude: float
    description_brief: str
    description_detail: str


class PostResponse(Post):
    id: str = Field(default_factory=str)


# ---------------------
# Routes
# ---------------------

@app.get("/")
def read_root():
    return {"message": "Blogger API is running!"}


# Create Post
@app.post("/posts", response_model=PostResponse)
async def create_post(post: Post):
    result = await db.posts.insert_one(post.dict())
    return {**post.dict(), "id": str(result.inserted_id)}


# Get All Posts
@app.get("/posts", response_model=List[PostResponse])
async def get_posts():
    posts = await db.posts.find().to_list(100)
    return [{**p, "id": str(p["_id"])} for p in posts]


# Get Single Post by ID
@app.get("/posts/{post_id}", response_model=PostResponse)
async def get_post(post_id: str):
    post = await db.posts.find_one({"_id": ObjectId(post_id)})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return {**post, "id": str(post["_id"])}


# Update Post
@app.put("/posts/{post_id}", response_model=PostResponse)
async def update_post(post_id: str, post: Post):
    result = await db.posts.update_one(
        {"_id": ObjectId(post_id)}, {"$set": post.dict()}
    )
    if result.modified_count == 0:
        raise HTTPException(
            status_code=404, detail="Post not found or no changes made"
        )
    updated = await db.posts.find_one({"_id": ObjectId(post_id)})
    return {**updated, "id": str(updated["_id"])}


# Delete Post
@app.delete("/posts/{post_id}")
async def delete_post(post_id: str):
    result = await db.posts.delete_one({"_id": ObjectId(post_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"message": "Post deleted successfully"}
