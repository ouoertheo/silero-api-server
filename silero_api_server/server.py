
import pathlib
import os
from fastapi import FastAPI, Response, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
from silero_api_server.tts import SileroTtsService
from loguru import logger
from typing import Optional

module_path = pathlib.Path(__file__).resolve().parent
os.chdir(module_path)
SAMPLE_PATH = pathlib.Path("samples")

tts_service = SileroTtsService(f"{module_path}//{SAMPLE_PATH}")
app = FastAPI()

# Make sure the samples directory exists
if not SAMPLE_PATH.exists():
    SAMPLE_PATH.mkdir()

if len(list(SAMPLE_PATH.iterdir())) == 0:
    logger.info("Samples empty, generating new samples.")
    tts_service.generate_samples()

app.mount(f"/samples",StaticFiles(directory=module_path.joinpath(SAMPLE_PATH)),name='samples')
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
    session: Optional[str]

class SampleText(BaseModel):
    text: Optional[str]

class SessionPayload(BaseModel):
    path: Optional[str]

@app.get("/tts/speakers")
def speakers(request: Request):
    voices = [
        {
            "name":speaker,
            "voice_id":speaker,
            "preview_url": f"{str(request.base_url)}{SAMPLE_PATH}/{speaker}.wav"
        } for speaker in tts_service.get_speakers()
    ]
    return voices

@app.post("/tts/generate")
def generate(voice: Voice):
    # Clean elipses
    voice.text = voice.text.replace("*","")
    try:
        if voice.session:
            audio = tts_service.generate(voice.speaker, voice.text, voice.session)
        else:
            audio = tts_service.generate(voice.speaker, voice.text)
        return FileResponse(audio)
    except Exception as e:
        logger.error(e)
        return HTTPException(500,f"{voice.speaker} generation failed: {e}")
    
@app.get("/tts/sample")
def play_sample(speaker: str):
    return FileResponse(f"{SAMPLE_PATH}/{speaker}.wav")

@app.post("/tts/generate-samples")
def generate_samples(sample_text: Optional[str] = ""):
    tts_service.update_sample_text(sample_text)
    tts_service.generate_samples()
    return Response("Generated samples",status_code=200)

@app.post("/tts/init_session")
def init_session(sessionPayload: SessionPayload):
    tts_service.init_sessions_path(sessionPayload.path)
    return Response(f"Session path created at {sessionPayload.path}")

if __name__ == "__main__":
    uvicorn.run(app,host="0.0.0.0",port=8001)
