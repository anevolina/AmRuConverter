from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from dotenv import load_dotenv
import logging
import os
from os.path import join, dirname

from googletrans import Translator
from converter import ARConverter

# start logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

# Load .env & token for the bot
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
TLGR_TOKEN = os.environ.get('TLGR_TOKEN')

# Initialize updater and dispatcher... as like I know what it is
updater = Updater(token=TLGR_TOKEN)
dispatcher = updater.dispatcher

# Initialize converter and translator
my_converter = ARConverter()
my_translator = Translator(service_urls=[
      'translate.google.com',
      'translate.google.co.kr',
    ])


# define reaction to /start command in tlgr
def start_callback(bot, update):
    update.message.reply_text('Введи сообщение')

def am_ru_convert(bot, update):
    text = update.message.text.split('\n')
    my_recipe = ''

    for line in text:

        my_recipe += my_converter.process_line(line) + '\n'

    bot_answer = my_translator.translate(my_recipe, dest='ru')

    bot.send_message(chat_id=update.message.chat_id, text=bot_answer.text)


# define all handlers
start_handler = CommandHandler("start", start_callback)
answer_handler = MessageHandler(Filters.text, am_ru_convert)

# adding handlers to our dispatcher
dispatcher.add_handler(start_handler)
dispatcher.add_handler(answer_handler)

# and start the bot...
updater.start_polling()

