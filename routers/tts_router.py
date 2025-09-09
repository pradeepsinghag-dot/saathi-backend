# routers/tts_router.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from bson import ObjectId
from db import db  # your MongoDB instance
import pyttsx3
import tempfile
import os

router = APIRouter(
    prefix="/tts",
    tags=["TTS"]
)

@router.get("/post/{post_id}")
async def tts_post(post_id: str):
    # Validate ObjectId
    try:
        oid = ObjectId(post_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid post ID")

    # Fetch post from MongoDB
    post = await db.posts.find_one({"_id": oid})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    text = post.get("description_detail", "")
    if not text:
        raise HTTPException(status_code=404, detail="No description available")

    # Offline TTS with pyttsx3
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)  # optional: speech speed
    engine.setProperty('volume', 1.0)  # optional: volume

    # Use a temporary file to store the MP3
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        engine.save_to_file(text, f.name)
        engine.runAndWait()
        filename = f.name

    # Return the MP3 as a streaming response
    response = FileResponse(
        path=filename,
        media_type="audio/mpeg",
        filename="tts.mp3"
    )

    # Clean up temporary file after response
    @response.background
    def cleanup():
        if os.path.exists(filename):
            os.remove(filename)

    return response
