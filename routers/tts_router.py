# routers/tts_router.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from gtts import gTTS
from bson import ObjectId
from db import db  # your MongoDB instance
import io

router = APIRouter(
    prefix="/tts",
    tags=["TTS"]
)

@router.get("/post/{post_id}")
async def tts_post(post_id: str):
    # Convert string to ObjectId
    try:
        oid = ObjectId(post_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid post ID")

    post = await db.posts.find_one({"_id": oid})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    text = post.get("description_detail", "")
    if not text:
        raise HTTPException(status_code=404, detail="No description available")

    # Convert text to speech
    tts = gTTS(text=text, lang="en")
    mp3_fp = io.BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)

    return StreamingResponse(mp3_fp, media_type="audio/mpeg")
