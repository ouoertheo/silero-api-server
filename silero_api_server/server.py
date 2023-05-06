
import dotenv, os
from fastapi import FastAPI, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from silero_api_server.tts import SileroTtsService
from loguru import logger
dotenv.load_dotenv()
HOSTNAME = os.getenv('TTS_SERVER_HOSTNAME')
PORT = os.getenv('TTS_SERVER_PORT')
LOCAL_URL = f"http://{HOSTNAME}:{PORT}"

app = FastAPI()

# Make sure the samples directory exists
if not os.path.exists('samples'):
    os.mkdir('samples')

app.mount('/samples',StaticFiles(directory='samples'),name='samples')
tts_service = SileroTtsService()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Voice(BaseModel):
    speaker: str
    text: str

class SampleText(BaseModel):
    text: str | None

@app.get("/tts/speakers")
def speakers():
    voices = [
        {
            "name":speaker,
            "voice_id":speaker,
            "preview_url": f"{LOCAL_URL}/samples/{speaker}.wav"
        } for speaker in tts_service.get_speakers()
    ]
    return voices

@app.post("/tts/generate")
def generate(voice: Voice):
    try:
        audio = tts_service.generate(voice.speaker, voice.text)
        return FileResponse(audio)
    except Exception as e:
        logger.error(e)
        return HTTPException(500,voice.speaker)
    
@app.get("/tts/sample")
def play_sample(speaker: str):
    return FileResponse(f"samples/{speaker}.wav")

@app.post("/tts/generate-samples")
def generate_samples(sample_text: str):
    tts_service.update_sample_text(sample_text)
    tts_service.generate_samples()
    return Response("Generated samples",status_code=200)