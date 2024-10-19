import uvicorn
from  silero_api_server.server import app, tts_service

import argparse

parser = argparse.ArgumentParser(
                    prog='silero_api_server',
                    description='Run Silero within a FastAPI application')
parser.add_argument('-o','--host', action='store', dest='host', default='0.0.0.0')
parser.add_argument('-p','--port', action='store', dest='port', type=int, default=8001)
parser.add_argument('-s','--session_path', action='store', dest='session_path', type=str, default="sessions")
parser.add_argument('-l','--language', action='store', dest='language', type=str, default="v3_en.pt")
parser.add_argument('--show-languages', action='store_true', dest='show_languages')

args = parser.parse_args()

if help not in args:
    if args.show_languages:
        for lang in tts_service.langs.keys():
            print(lang)
    else:
        tts_service.load_model(args.language)
        uvicorn.run(app, host=args.host, port=args.port)
