FROM python:3.10-slim

ARG DISCORD_TOKEN
ENV DISCORD_TOKEN=$DISCORD_TOKEN

WORKDIR /app
COPY . /app
RUN apt-get update && apt-get install -y ffmpeg
RUN pip install --upgrade pip
# Install yt-dlp
RUN pip install yt-dlp
RUN python3 -m pip install --force-reinstall https://github.com/yt-dlp/yt-dlp/archive/master.tar.gz
RUN pip install poetry
RUN poetry install

CMD ["poetry", "run", "music-bot"]
