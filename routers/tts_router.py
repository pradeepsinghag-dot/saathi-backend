from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from gtts import gTTS
from db import db
from bson import ObjectId
import io
import asyncio
from concurrent.futures import ThreadPoolExecutor
import re

router = APIRouter(prefix="/tts", tags=["TTS"])

# Thread pool for blocking TTS operations
executor = ThreadPoolExecutor(max_workers=4)

def split_into_sentences(text):
    """Split text into sentences using regex"""
    # Simple sentence splitting regex (can be improved)
    sentences = re.split(r'(?<=[.!?]) +', text)
    return sentences

def generate_tts_chunk(text, lang="en"):
    """Generate TTS for a chunk of text"""
    tts = gTTS(text=text, lang=lang, slow=False)
    mp3_fp = io.BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    return mp3_fp.read()

async def stream_tts(text, lang="en", chunk_size=2):
    """Stream TTS by generating audio in chunks"""
    # Split text into sentences
    sentences = split_into_sentences(text)
    
    # Process in chunks to avoid long generation times
    for i in range(0, len(sentences), chunk_size):
        chunk = " ".join(sentences[i:i+chunk_size])
        
        # Generate TTS for this chunk in a thread pool
        loop = asyncio.get_event_loop()
        audio_data = await loop.run_in_executor(
            executor, generate_tts_chunk, chunk, lang
        )
        
        # Yield the audio data
        yield audio_data

@router.get("/post/{post_id}")
async def tts_post(post_id: str):
    # Fetch post from MongoDB
    post = await db.posts.find_one({"_id": ObjectId(post_id)})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    text_brief = post.get("description_brief", "")
    text_detail = post.get("description_detail", "")
    text = f"{text_brief}. {text_detail}".strip()

    if not text:
        raise HTTPException(status_code=400, detail="No text found in post")
    
    # Stream the TTS response
    return StreamingResponse(
        stream_tts(text, lang="en"),
        media_type="audio/mpeg"
    )

@router.get("/post/{post_id}/stream")
async def tts_post_stream(post_id: str):
    """Alternative implementation that streams sentence by sentence"""
    # Fetch post from MongoDB
    post = await db.posts.find_one({"_id": ObjectId(post_id)})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    text_brief = post.get("description_brief", "")
    text_detail = post.get("description_detail", "")
    text = f"{text_brief}. {text_detail}".strip()

    if not text:
        raise HTTPException(status_code=400, detail="No text found in post")
    
    # Split into sentences
    sentences = split_into_sentences(text)
    
    async def generate_audio():
        for sentence in sentences:
            if sentence.strip():  # Skip empty sentences
                # Generate TTS for this sentence
                loop = asyncio.get_event_loop()
                audio_data = await loop.run_in_executor(
                    executor, generate_tts_chunk, sentence, "en"
                )
                yield audio_data
    
    return StreamingResponse(
        generate_audio(),
        media_type="audio/mpeg"
    )