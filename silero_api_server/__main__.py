import uvicorn
from  silero_api_server.server import app

import argparse

parser = argparse.ArgumentParser(
                    prog='silero_api_server',
                    description='Run Silero within a FastAPI application')
parser.add_argument('-o','--host', action='store', dest='host', default='0.0.0.0')
parser.add_argument('-p','--port', action='store', dest='port', type=int, default=8001)

args = parser.parse_args()

if not args.help:
    uvicorn.run(app, host=args.host, port=args.port)