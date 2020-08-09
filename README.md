# Telegram Bot - Voice&Photo Grabber

This is a Telegram Bot that allows you to save voice messages and photos with faces. 

# Getting Started

```
git clone git@github.com:xredian/telegram-audio-photo.git
```

# Creating .env

Before installation you need to create **.env** file as in an example below.

```
# token for telegram bot
TOKEN=your-bot-token
```

# Installation

Create Docker build for bot.
```
docker build -t app-tg-bot -f Dockerfile .
```

# Creating virtual environment
```
docker-compose up 
```

# Usage

After starting the bot, you can add it to your chats. 
Then bot will save all voice messages to you storage in folders according to uid. 
All saved voice messages are recorded in the database.
Also bot will save to your storage all photos with faces on it.

## Authors

* **Uliana Diakova** - *Test project* - [xredian](https://github.com/xredian)
