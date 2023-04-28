# A simple FastAPI Server to run Silero TTS
[Silero PyTorch Page](https://pytorch.org/hub/snakers4_silero-models_tts/)
[Silero GitHub Page](https://github.com/snakers4/silero-models)

## Installation
Recommended to use venv. You can run using the following commands. Change the script name if you are running from cmd or bash
```
py -m venv .\venv
.\venv\scripts\Activate.ps1
pip install -r requirements.txt
```

## Configuration
The server runs on `localhost:8001` by default. You can leave IP at 0.0.0.0 to listen on all IPs.
Ports will be updated in the `run` script. Port and hostname will be updated in `.env` file. 

On first run of server, the model will need to be downloaded, this will happen automatically and may take a few minutes depending on your connection speed.

## Starting Server
Enter the venv `.\venv\scripts\Activate.ps1`
Execute the included `run.ps1` or `run.sh`
You can access the API spec at `http://localhost:8001/docs`

## Voice Samples
Samples must be generated by a POST command to `/generate-samples`  (easy way to run is from http://localhost:8001/docs)
Samples are served statically by the web server at `/samples/{speaker}.wav` or callable from the API from `/tts/sample?speaker={speaker}` endpoint