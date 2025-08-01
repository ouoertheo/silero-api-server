# A simple FastAPI Server to run Silero TTS
Credit goes to the developers of Silero TTS  
[Silero PyTorch Page](https://pytorch.org/hub/snakers4_silero-models_tts/)  
[Silero GitHub Page](https://github.com/snakers4/silero-models)

## Installation
`pip install silero-api-server`

## Starting Server
`python -m silero_api_server` will run on default ip and port (0.0.0.0:8001)

```
usage: silero_api_server [-h] [-o HOST] [-p PORT]

Run Silero within a FastAPI application

options:
  -h, --help            show this help message and exit
  -o HOST, --host HOST
  -p PORT, --port PORT
  -l LANG, --language LANG
  --show-languages
```

On first run of server, two operations occur automatically. These may take a minute or two.
1. The model will be downloaded 
2. Voice samples will be generated. 

## Deploying server as a container

You can build an image from current source by running `docker build -t silero:latest .` in the top
level of repository. Server can then be deployed as a container with `docker run -p 8001:8001 silero:latest`.

# API Docs
API Docs can be accessed from [http://localhost:8001/docs](http://localhost:8001/docs)

# Voice Samples
Samples are served statically by the web server at `/samples/{speaker}.wav` or callable from the API from `/tts/sample?speaker={speaker}` endpoint.

# Selecting Language
Use command-line options or download and set the desired language using `POST /tts/language` with payload `{"id":"languageId"}`  
List of language ids are available via `GET /tts/language`
