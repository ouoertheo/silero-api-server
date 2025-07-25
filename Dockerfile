FROM ubuntu:22.04
RUN apt update && apt install -y python3-pip git
COPY . .
RUN pip install . 
CMD ["python3", "-m", "silero_api_server"]
