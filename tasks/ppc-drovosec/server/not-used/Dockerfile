FROM python:3.10

#upgrade ffmpeg for aiortc av dependency
RUN apt-get update && apt-get install -y software-properties-common
RUN apt-get install python3-launchpadlib -y && add-apt-repository ppa:jonathonf/ffmpeg-4
RUN apt-get update && apt-get upgrade -y

#install aiortc dependencies
RUN apt-get install -y \
    libavdevice-dev \
    libavfilter-dev \
    libopus-dev \
    libvpx-dev \
    libsrtp2-dev \
    pkg-config

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT uvicorn src.app:app --host 0.0.0.0 --port 5000
