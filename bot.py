from collections import defaultdict
from dotenv import load_dotenv
import logging
import os
import psycopg2
import subprocess
import telegram
from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters)
from telegram.ext.callbackcontext import CallbackContext


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

print("Database opened successfully")
try:
    cur.execute("CREATE TABLE audio_messages (uid text, messages text PRIMARY KEY);")
except:
    print("I can't create a table!")

con.commit()


def start(update, context):
    reply_keyboard = [['/start', '/help']]
    update.message.reply_text(
        "Hi, I can collect audio messages and photos with faces from groups or chats",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard))


def help_reply(update, context):
    update.message.reply_text(
        "Hey, you can add me to your group or chat to collect audio messages and photos with faces")


'''
# echo is needed to be used as a chat bot
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
'''


def error(update: Updater, context: CallbackContext):
    logger.warning('Update "{u}" caused error "{e}"'.format(u=update, e=context.error))


audio_msgs = defaultdict()
num = 0
cur_dir = os.getcwd()
user_id = ''


def audio_messages(update, context):
    """
    Download voice messages from dialogs where bot is added
    :param update: Updater
    :param context: CallbackContext
    :return: oga_to_wav() which convert .oga file to .wav file with a sampling rate of 16 kHz
    """
    msg = update.message.voice
    global user_id
    # user_id = update.message.from_user.username looks better with username, but the terms of reference says to use id
    user_id = str(update.message.from_user.id)
    print(user_id)
    if user_id not in audio_msgs.keys():
        audio_msgs[user_id] = 0
    else:
        audio_msgs[user_id] += 1
    global num
    num = audio_msgs[user_id]
    try:
        new_dir = cur_dir + '/' + user_id
        os.mkdir(new_dir)
        os.chdir(new_dir)
    except OSError:
        new_dir = cur_dir + '/' + user_id
        os.chdir(new_dir)
    voice = bot.get_file(msg.file_id).download(f'audio_message_{num}.oga')
    return oga_to_wav()


uid_mes = defaultdict(list)


def oga_to_wav():
    """
    Convert .oga file to .wav file with a sampling rate of 16 kHz
    :return: db_rec() which make a record to DB
    """
    src_filename = f'audio_message_{num}.oga'
    dest_filename = f'audio_message_{num}.wav'
    uid_mes[user_id].append(dest_filename)

    process = subprocess.run(['ffmpeg', '-i', src_filename, '-ar', '16000', dest_filename])
    if process.returncode != 0:
        raise Exception("Something went wrong")
    os.remove(src_filename)
    os.chdir(cur_dir)
    return db_rec()


def db_rec():
    """
    Make a record to DB
    :return: None
    """
    cur.execute("""
    DO $$
    BEGIN
        LOOP
            UPDATE audio_messages SET messages = %s WHERE uid = %s;
            IF found THEN 
                RETURN;
                END IF;
            BEGIN 
                INSERT INTO audio_messages(uid, messages) VALUES (%s, %s);
                RETURN;
            EXCEPTION WHEN unique_violation THEN
            END;
        END LOOP;
    END; 
    $$
    LANGUAGE plpgsql;""", (uid_mes[user_id], user_id, user_id, uid_mes[user_id]))


def main():
    updater = Updater(bot_token, request_kwargs=REQUEST_KWARGS, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', help_reply))
    # dp.add_handler(MessageHandler(Filters.text, echo))
    dp.add_handler(MessageHandler(Filters.voice, audio_messages))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
