# V3
import os, time
import shutil
import requests
import torch
import torch.package
import torchaudio
from hashlib import md5
from loguru import logger
from pydub import AudioSegment
from pathlib import Path
import json

class SileroTtsService:
    """
    Generate TTS wav files using Silero
    """
    def __init__(self, sample_path, lang="v3_en.pt") -> None:
        self.sample_text = "The fallowed fallen swindle auspacious goats in portable power stations."
        self.sample_path = Path(sample_path)
        self.sessions_path = None

        # Silero works fine on CPU
        self.device = torch.device('cpu')
        torch.set_num_threads(4)
        torchaudio.set_audio_backend("soundfile")

        # Make sure we have the sample path
        if not self.sample_path.exists():
            self.sample_path.mkdir()   

        self.sample_rate = 48000 
        logger.info(f"TTS Service loaded successfully")

        # Prevent generation failure due to too long input
        self.max_char_length = 600

        # Get language model URLs
        self.langs = self.list_languages()

        # Load model
        self.load_model(lang)

    def init_sessions_path(self, sessions_path="sessions"):
        self.sessions_path = Path(sessions_path)
        if not self.sessions_path.exists():
            self.sessions_path.mkdir()
    
    def load_model(self, lang_model="v3_en.pt"):
        # Download the model. Default to en.
        if lang_model not in self.langs:
            raise Exception(f"{lang_model} not in {list(self.langs.values())}")
        
        model_url = self.langs[lang_model]
        self.model_file = Path(lang_model)

        if not Path.is_file(self.model_file):
            logger.warning(f"Downloading Silero {lang_model} model...") 
            torch.hub.download_url_to_file(model_url,
                                        self.model_file)  
            logger.info(f"Model download completed.")
        
        self.model = torch.package.PackageImporter(self.model_file).load_pickle("tts_models", "model")
        self.model.to(self.device)

    def generate(self, speaker, text, session=""):
        if len(text) > self.max_char_length:
            # Handle long text input
            text_chunks = self.split_text(text)
            combined_wav = AudioSegment.empty()

            for chunk in text_chunks:
                audio_path = Path(self.model.save_wav(text=chunk,speaker=speaker,sample_rate=self.sample_rate))
                combined_wav += AudioSegment.silent(500) # Insert 500ms pause
                combined_wav += AudioSegment.from_file(audio_path)

            combined_wav.export("test.wav", format="wav")
            audio_path = Path("test.wav")
        else:
            audio_path = Path(self.model.save_wav(text=text,speaker=speaker,sample_rate=self.sample_rate))
        if session:
            self.save_session_audio(audio_path, session, speaker)
        return audio_path

    def split_text(self, text:str) -> list[str]:
        # Split text into chunks less than self.max_char_length
        chunk_list = []
        chunk_str = ""

        for word in text.split(' '):
            word = word.replace('\n',' ') + " "
            if len(chunk_str + word) > self.max_char_length:
                chunk_list.append(chunk_str)
                chunk_str = ""
            chunk_str += word
        
        # Add the last chunk
        if len(chunk_str) > 0:
            chunk_list.append(chunk_str)

        return chunk_list


    def combine_audio(self, audio_segments):
        combined_audio = AudioSegment.from_mono_audiosegments(audio_segments)
        return combined_audio

    def save_session_audio(self, audio_path:Path, session:Path, speaker):
        if not self.sessions_path:
            raise Exception("Session not initialized. Call /tts/init_session with {'path':'desired\session\path'}")
        session_path = self.sessions_path.joinpath(session)
        if not session_path.exists():
            session_path.mkdir()
        dst = session_path.joinpath(f"tts_{session}_{int(time.time())}_{speaker}_.wav")
        shutil.copy(audio_path, dst)

    def get_speakers(self):
        "List different speakers in model"
        return self.model.speakers

    def generate_samples(self):
        "Remove current samples and generate new ones for all speakers."
        logger.warning("Removing current samples")
        for file in self.sample_path.iterdir():
            os.remove(self.sample_path.joinpath(file))

        logger.info("Creating new samples. This should take a minute...")
        for speaker in self.model.speakers: 
            sample_name = Path(self.sample_path.joinpath(f"{speaker}.wav"))
            if sample_name.exists():
                continue
            audio = Path(self.model.save_wav(text=self.sample_text,speaker=speaker,sample_rate=self.sample_rate))
            audio.rename(self.sample_path.joinpath(sample_name))
        logger.info("New samples created")

    def update_sample_text(self,text: str):
        "Update the text used to generate samples"
        if not text: return
        self.sample_text = text
        logger.info(f"Sample text updated to {self.sample_text}")  

    def list_languages(self):
        'Grab all v3 model links from https://models.silero.ai/models/tts'
        lang_file = Path('langs.json')
        if lang_file.exists():
            with lang_file.open('r') as fh:
                logger.info('Loading cached language index')
                return json.load(fh)
        logger.info('Loading remote language index')
        lang_base_url = 'https://models.silero.ai/models/tts'
        lang_urls = {}

        # Parse initial web directory for languages
        response = requests.get(lang_base_url)
        langs = [lang.split('/')[0] for lang in response.text.split('<a href="')][1:]

        # Enter each web directory and grab v3 model file links
        for lang in langs:
            response = requests.get(f"{lang_base_url}/{lang}")
            if not response.ok:
                raise f"Failed to get languages: {response.status_code}"
            lang_files = [f.split('"')[0] for f in response.text.split('<a href="')][1:]

            # If a valid v3 file, add to list
            for lang_file in lang_files:
                if lang_file.startswith('v3'):
                    lang_urls[lang_file]=f"{lang_base_url}/{lang}/{lang_file}"
        with open('langs.json','w') as fh:
            json.dump(lang_urls,fh)
        return lang_urls