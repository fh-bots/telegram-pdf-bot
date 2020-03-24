# -*- coding: utf-8 -*-

"""
Simple Bot to reply to Telegram messages.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import os
import logging

import img2pdf
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def echo(update, context):
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def convert_image(update, context):
    """Convert the sent image to pdf and send it back."""
    file_id = update.message.document.file_id
    file_name = update.message.document.file_name
    new_file = context.bot.get_file(file_id)
    temp_name = os.path.join("/mnt/ramdisk", file_id + file_name)
    print(temp_name)
    new_file.download(custom_path=temp_name)
    print("File saved")
    with open(temp_name + ".pdf", "wb") as f:
        f.write(img2pdf.convert(temp_name))
    context.bot.send_document(
        chat_id=update.effective_chat.id, document=open(temp_name + ".pdf", 'rb'), file_name=file_name)
    print("File send")
    os.remove(temp_name)
    os.remove(temp_name + ".pdf")
    print("File removed")


def info_photo(update, context):
    """Send info that one should send images as files."""
    update.message.reply_text("Please send images as files.")


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))
    dp.add_handler(MessageHandler(Filters.document.category("image"), convert_image))
    dp.add_handler(MessageHandler(Filters.photo, info_photo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()