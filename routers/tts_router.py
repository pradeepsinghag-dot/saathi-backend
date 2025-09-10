from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from gtts import gTTS
import io

router = APIRouter(prefix="/tts", tags=["TTS"])

@router.get("/speak")
async def speak(text: str):
    """
    Converts the given text to speech (MP3) and streams it.

    Query Parameters:
        text: str - The text to convert to speech
    """
    if not text:
        raise HTTPException(status_code=400, detail="Text parameter is required")
    
    try:
        # Generate speech using gTTS
        tts = gTTS(text=text, lang="en")
        
        # Save to a BytesIO object (in-memory)
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        
        # Stream the MP3 file as a response
        return StreamingResponse(mp3_fp, media_type="audio/mpeg")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS generation failed: {e}")
