
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
SAMPLE_PATH = "samples"
SESSION_PATH = "sessions"

tts_service = SileroTtsService(f"{module_path}//{SAMPLE_PATH}", SESSION_PATH)
app = FastAPI()

# Make sure the samples directory exists
if not os.path.exists(SAMPLE_PATH):
    os.mkdir(SAMPLE_PATH)

if len(os.listdir(SAMPLE_PATH)) == 0:
    logger.info("Samples empty, generating new samples.")
    tts_service.generate_samples()

app.mount(f"/samples",StaticFiles(directory=f"{module_path}//{SAMPLE_PATH}"),name='samples')
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
        return HTTPException(500,voice.speaker)
    
@app.get("/tts/sample")
def play_sample(speaker: str):
    return FileResponse(f"{SAMPLE_PATH}/{speaker}.wav")

@app.post("/tts/generate-samples")
def generate_samples(sample_text: Optional[str] = ""):
    tts_service.update_sample_text(sample_text)
    tts_service.generate_samples()
    return Response("Generated samples",status_code=200)

if __name__ == "__main__":
    uvicorn.run(app,host="0.0.0.0",port=8001)
