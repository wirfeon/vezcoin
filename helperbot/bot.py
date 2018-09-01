#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import requests
import json
import os
from copy import copy
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from datetime import datetime
import base64
import time

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

logger = logging.getLogger(__name__)

_port = int(os.environ["PORT"])
_webhook = os.environ["WEB_HOOK"]
_token = os.environ["BOT_TOKEN"]
_location = os.environ["URL_LOCATION"]
_certificate = os.environ["CERTIFICATE"]
_listen = "127.0.0.1"

logbook = None
logset = set()

source = -1001250812844
target = -277123461 

def chat(bot, update):
    global logbook, logset

    if (update.message.chat.id != source):
        return

    if (not update.message.from_user.username):
        return

    if (update.message.from_user.username not in logset):
        bot.send_message(target, "@%s" % update.message.from_user.username)
        update.message.reply_text("An admin assist respond with assistace within 24 hrs.")
        logset.add(update.message.from_user.username)  
        logbook.write("%s\n" % update.message.from_user.username)
        logbook.flush()
    else:
        if (update.message.entities):
            for entity in update.message.entities:
                if (update.message.text[entity["offset"] : entity["offset"] + entity["length"]] == "@admin"):
                    update.message.reply_text("An admin assist respond with assistace within 24 hrs.")
                    break
        
def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

def main():
    global logbook, logset

    try:
        logbook = open("data/logbook.txt", "a+")
        logbook.seek(0, 0)
        
        for line in logbook.readlines():
            logset.add(line.strip())
            logger.info(line)

        logger.info(logset)
    except Exception as e:
        logger.warn("Exception: %s" % e)


    updater = None

    i = 0
    while i < 2:
        try:
            # Create the EventHandler and pass it your bot's token.
            updater = Updater(_token, workers = 1)

            logger.info("Starting webhook '%s' %d '%s'" % (_listen, _port, _location))
            updater.start_webhook(listen=_listen, port=_port, url_path=_location)
            updater.bot.set_webhook(url=_webhook, certificate=open(_certificate, 'rb'))
            break
        except Exception as e:
            logger.warn("Exception: %s" % e)
            if (updater):
                updater.stop()
        #endtry
        
        i += 1
        time.sleep(1)
    #endwhile

    if (not updater):
        return

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.text, chat))

    # log all errors
    dp.add_error_handler(error)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    logger.info("Running")
    updater.idle()

    logger.info("Stoping updater") 
    updater.stop()

    logbook.close()
 
if __name__ == '__main__':
    main()
