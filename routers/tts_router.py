from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from gtts import gTTS
from db import db  # your MongoDB connection
from bson import ObjectId
import io

router = APIRouter(prefix="/tts", tags=["TTS"])

@router.get("/post/{post_id}")
async def tts_post(post_id: str):
    # Fetch post from MongoDB
    post = await db.posts.find_one({"_id": ObjectId(post_id)})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # text = post.get("description_brief", "")
    text_brief = post.get("description_brief", "")
    text_detail = post.get("description_detail", "")

# Combine both, separated by a pause/period
    text = f"{text_brief}. {text_detail}".strip()


    if not text:
        raise HTTPException(status_code=400, detail="No text found in post")
    
    # Generate TTS
    tts = gTTS(text=text, lang="en")
    mp3_fp = io.BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    
    return StreamingResponse(mp3_fp, media_type="audio/mpeg")
