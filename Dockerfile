FROM python:3.8.6-buster
COPY . /app
RUN ls -la /app
RUN pip install -r /app/requirements.txt
RUN apt-get update
RUN apt-get install ffmpeg vlc alsa-utils pulseaudio -y
CMD python3 /app/SpeakerBot.py