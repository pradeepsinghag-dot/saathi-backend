from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from bson import ObjectId
from db import db
import pyttsx3
import io
import logging
import tempfile
import os

router = APIRouter(prefix="/tts", tags=["TTS"])

logging.basicConfig(level=logging.DEBUG)

# Initialize engine globally (better than creating per-request)
engine = pyttsx3.init()
engine.setProperty("rate", 160)   # Adjust speech speed
engine.setProperty("volume", 1.0) # Max volume

voices = engine.getProperty("voices")
if voices:
    engine.setProperty("voice", voices[0].id)  # Pick first available voice

@router.get("/post/{post_id}")
async def tts_post(post_id: str):
    try:
        oid = ObjectId(post_id)
    except Exception as e:
        logging.error(f"Invalid ObjectId: {e}")
        raise HTTPException(status_code=400, detail="Invalid post ID")

    post = await db.posts.find_one({"_id": oid})
    if not post:
        logging.error(f"Post not found: {post_id}")
        raise HTTPException(status_code=404, detail="Post not found")

    text = post.get("description_detail", "")
    if not text:
        logging.error("No description available")
        raise HTTPException(status_code=404, detail="No description available")

    try:
        # Create temporary file in /tmp (safe for Render)
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav", dir="/tmp")
        tmp_file.close()

        # Generate TTS
        engine.save_to_file(text, tmp_file.name)
        engine.runAndWait()
        logging.info(f"Audio generated: {tmp_file.name}")

        def iterfile():
            with open(tmp_file.name, mode="rb") as f:
                while chunk := f.read(4096):
                    yield chunk
            os.remove(tmp_file.name)  # cleanup

        return StreamingResponse(iterfile(), media_type="audio/wav")

    except Exception as e:
        logging.error(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=f"TTS error: {e}")
