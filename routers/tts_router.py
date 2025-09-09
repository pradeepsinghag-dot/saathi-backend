from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from bson import ObjectId
from db import db
import pyttsx3
import io
import logging

router = APIRouter(prefix="/tts", tags=["TTS"])

logging.basicConfig(level=logging.DEBUG)

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
        mp3_fp = io.BytesIO()
        engine = pyttsx3.init()

        # Optional: check available voices
        voices = engine.getProperty('voices')
        logging.debug(f"Available voices: {[v.name for v in voices]}")

        engine.save_to_file(text, 'temp_audio.wav')
        engine.runAndWait()
        logging.info("Audio generated successfully")

        # Read the file and stream
        with open('temp_audio.wav', 'rb') as f:
            mp3_fp.write(f.read())
        mp3_fp.seek(0)

        return StreamingResponse(mp3_fp, media_type="audio/wav")

    except Exception as e:
        logging.error(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=f"TTS error: {e}")
