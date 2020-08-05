from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters)
from telegram.ext.callbackcontext import CallbackContext
from telegram import (ReplyKeyboardMarkup)
import logging
import subprocess
import telegram
import psycopg2
import os
from dotenv import load_dotenv
from collections import defaultdict


load_dotenv()

# telegram bot token
bot_token = os.getenv("TOKEN")
bot = telegram.Bot(token=bot_token)


# logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

logger = logging.getLogger(__name__)


# proxy
REQUEST_KWARGS = {
    'proxy_url': os.getenv("PROXY"),
    'urllib3_proxy_kwargs': {
        'username': os.getenv("USPROXY"),
        'password': os.getenv("PASSPROXY"),
    }
}


# connection to db
con = psycopg2.connect(
        database="users_msgs",
        user=os.getenv("DBUSER"),
        password=os.getenv("DBPWD"),
        host="localhost",
        port="5432"
    )
con.autocommit = True
cur = con.cursor()


def start(update, context):
    reply_keyboard = [['/start', '/help']]
    update.message.reply_text(
        "Hi, I can collect audio messages and photos with faces from groups or chats",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard))


def help_reply(update, context):
    update.message.reply_text(
        "Hey, you can add me to your group or chat to collect audio messages and photos with faces")


def echo(update, context):
    text = update.message.text
    if text == '/start':
        return start(update, context)
    elif text == 'help':
        return help_reply(update, context)
    else:
        update.message.reply_text("I don't understand you. Please write /start or "
                                  "/help.")
        logger.info(update)


def error(update: Updater, context: CallbackContext):
    logger.warning('Update "{u}" caused error "{e}"'.format(u=update, e=context.error))


audio_msgs = defaultdict()


def audio_messages(update, context):
    msg = update.message.voice
    user_id = update.message.chat.username
    if str(user_id) not in audio_msgs.keys():
        audio_msgs[user_id] = 0
    else:
        audio_msgs[user_id] += 1
    global num
    num = audio_msgs[user_id]
    voice = bot.get_file(msg.file_id).download(f'audio_message_{num}.oga')
    return oga_to_wav(voice)


def oga_to_wav(voice):
    src_filename = f'audio_message_{num}.oga'
    dest_filename = f'audio_message_{num}.wav'

    process = subprocess.run(['ffmpeg', '-i', src_filename, '-ar', '16000', dest_filename])
    if process.returncode != 0:
        raise Exception("Something went wrong")


def main():
    updater = Updater(bot_token, request_kwargs=REQUEST_KWARGS, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', help_reply))
    dp.add_handler(MessageHandler(Filters.text, echo))
    dp.add_handler(MessageHandler(Filters.voice, audio_messages))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
