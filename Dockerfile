FROM python:3.7-stretch

# устанавливаем параметры сборки
RUN apt-get update && \
 apt-get install -y gcc make apt-transport-https ca-certificates build-essential

RUN apt-get install -y ffmpeg

# проверяем окружение python
RUN python3 --version
RUN pip3 --version

# задаем рабочую директорию для контейнера
WORKDIR /usr/src/app-tgbot-voice-photo

# устанавливаем зависимости python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY * /src/
RUN ls -la /src/*


CMD ["python3", "/src/bot.py"]
