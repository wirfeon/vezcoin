#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import json
import os
import time
import sys
from copy import copy
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, Handler
from telegram import Chat
from datetime import datetime
import requests
import random
import time

_port = int(os.environ['PORT'])
_webhook = "%s%s" % (os.environ["WEB_HOOK"], os.environ["BOT_TOKEN"])
_token = os.environ["BOT_TOKEN"]
_location = os.environ["URL_LOCATION"]
_certificate = os.environ["CERTIFICATE"]
_listen = "127.0.0.1"
_nis_address = os.environ["NIS_ADDRESS"]

# Enable logging
logging.basicConfig(stream=sys.stderr, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

logger = logging.getLogger(__name__)

target = set()
test_group = -253624939
lid = ""
nem_addr = ""
ts = time.time()
lottery = []
lottery_group = 0
lottery_file = None
log = []

def publish(bot):
    logger.info("Publish")

def dump_target():
    try:
        db = open("data/groups.txt", "w")

        for cid in target:
            db.write("%d\n" % cid)

        db.close()
    except Exception as e:
        logger.warn("Exception: %s" % e)

def new_chat_members(bot, update):
    global ts, log

    logger.info("Added to chat")

    if (time.time() > ts + 10):
        ts = time.time()
        smsg = update.message.chat.send_message(
"""
Welcome to the myCoinvest (CVZ) chat! 🌚🚀

Please read the pinned message at
https://t.me/MCVOfficial/10046 before you post.
""", disable_web_page_preview = True)

    log.append((ts, smsg.message_id, update.message.chat.id))    

    if (update.message.chat.id not in target):
        target.add(update.message.chat.id)
        dump_target()

def left_chat_member(bot, update):
    logger.info("Left chat")

    if (update.message.left_chat_member.id == bot.id):
        if (update.message.chat.id in target):
            target.remove(update.message.chat.id)
            dump_target()

def scrape(bot, update):
    global nem_addr, lid

    if (nem_addr):
        try:
            reply = requests.get(_nis_address + "/account/transfers/outgoing?address=" + nem_addr)
            reply = json.loads(reply.text)
            #logger.info(reply)
            
            report = []
            for txn in reply["data"]:
                if ("%s" % txn["meta"]["id"] == lid):
                    break

                report.append(txn)

            if (report):
                logger.info(report)
            
                for txn in reversed(report):
                    logger.info("%d" % txn["meta"]["id"])
                    
                    f = open("data/groups.txt", "r")
                    for group in f.readlines():
                        try:
                            for mosaic in txn["transaction"]["otherTrans"]["mosaics"]:
                                if (mosaic["mosaicId"]["name"] == "vezcoin"):
                                    amount = int(mosaic["quantity"] / 100)
                                    if (amount >= 20000):
                                        bot.send_message(int(group.strip()), "{:,} Vezcoin was just claimed for a bounty 💥🚀🌚".format(amount))
                        except Exception as e:
                            pass
            
                    f.close() 

                lid = "%s" % report[0]["meta"]["id"]
                f = open("data/lastid.txt", "w");
                f.write(lid)
                f.close()
        except Exception as e:
            logger.warn("Exception: %s" % e)

    while (log and log[0][0] + 40 <= time.time()):
        logger.info("Deleting %d %d" % (log[0][2], log[0][1]))
        bot.delete_message(log[0][2], log[0][1])
        log.pop(0)   

def reset(bot, update):
    logger.info("Reset")

    nem_addr = update.message.text.split("/reset")[1].strip()
    if (not nem_addr):
        return

    f = open("data/nemaddress.txt", "w")
    f.write(nem_addr)
    f.close()

    try:
        reply = requests.get(_nis_address + "/account/transfers/outgoing?address=" + nem_addr)
        reply = json.loads(reply.text)

        if (len(reply["data"]) > 0):
            lid = "%d" % reply["data"][0]["meta"]["id"]

            f = open("data/lastid.txt", "w");
            f.write(lid)
            f.close()
    except Exception as e:
        logger.warn("Exception: %s" % e)
        return

def fallback(bot, update):
    global lottery_group, lottery_file, lottery

    logger.info("Fallback '%s' %d", update.message.from_user.username, update.message.chat.id)
    logger.info("%d %d %d", update.message.chat.id == lottery_group, update.message.from_user.username != "leoinker", update.message.from_user.username not in lottery)

    if (update.message.chat.id == lottery_group and update.message.from_user.username not in ()):
        if (update.message.from_user.username not in lottery):
            logger.info("Adding candidate '%s' %d" % (update.message.from_user.username, len(lottery)))

            lottery.append(update.message.from_user.username)
            lottery_file.write("%s\n" % update.message.from_user.username)
            lottery_file.flush()

def start_lottery(bot, update):
    global lottery_group, lottery_file, lottery

    if (update.message.from_user.username in ("wirfeon", "leoinker")):
        f = open("data/lottery_group.txt", "w")
        f.write("%d" % update.message.chat.id)
        f.close()

        lottery_group = update.message.chat.id
        lottery = []
        lottery_file.close()
        lottery_file = open("data/lottery.txt", "w+")

def pick(bot, update):
    global lottery_group, lottery_file, lottery

    if (update.message.chat.id == lottery_group and update.message.from_user.username in ("wirfeon", "leoinker")):
        if (lottery):
            random.seed(time.time())
            i = random.randint(0, len(lottery) - 1) 
            update.message.chat.send_message("And the winner is...")
            time.sleep(3)
            update.message.chat.send_message("@%s" % lottery[i])

            lottery = []
            lottery_file.close()
            lottery_file = open("data/lottery.txt", "w+")
        else:
            update.message.chat.send_message("No eligible candidates")
   
def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.error('Update "%s" caused error "%s"', update, error)

def main():
    global lottery_group, lottery_file, lottery

    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    try:
        f = open("data/groups.txt", "r")
        line = f.readline()
        while line:
            try:
                target.add(int(line));
            except Exception as e:
                logger.warn("Exception: %s" % e)
            
            line = f.readline()
        
        f.close()
    except Exception as e:
        logger.warn("Exception: %s" % e)

    try:
        f = open("data/lastid.txt", "r")
        lid = f.read()
        f.close()

        f = open("data/nemaddress.txt", "r")
        nem_addr = f.read()
        f.close()
        
        f = open("data/lottery_group.txt", "r")
        lottery_group = int(f.read())
        f.close()
    except Exception as e:
        logger.warn("Exception: %s" % e)

    try:
        lottery_file = open("data/lottery.txt", "a+")
        lottery_file.seek(0, 0)
        line = lottery_file.readline()
        
        while line:
            logger.info("Reading lottery: '%s'" % line.strip())
            lottery.append(line.strip())
            line = lottery_file.readline()

    except Exception as e:
        logger.warn("Exception: %s" % e)
 
    logger.info("Creating updater object with token: '%s'" % (_token))

    updater = Updater(_token)

    i = 0
    while i < 3:
        try:
            logger.info("Starting webhook '%s' %d '%s'" % (_listen, _port, _location))
            updater.start_webhook(listen=_listen, port=_port, url_path=_location)
            logger.info("Setting webhook with certificate '%s'" % (_certificate))
            updater.bot.set_webhook(url=_webhook, certificate=open(_certificate, 'rb'), timeout=5000)
            break
        except Exception as e:
            logger.error("Exception: %s" % e)
            updater.stop()

        i += 1
        time.sleep(2)
    #endwhile
 
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("reset", reset))
    dp.add_handler(CommandHandler("start_lottery", start_lottery))
    dp.add_handler(CommandHandler("pick", pick))
    dp.add_handler(MessageHandler(Filters.text, fallback))
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, new_chat_members))
    dp.add_handler(MessageHandler(Filters.status_update.left_chat_member, left_chat_member))

    # log all errors
    dp.add_error_handler(error)

    job = updater.job_queue
    job_sec = job.run_repeating(scrape, interval = 5, first = 0)

    logger.info("Running '%s' '%s'" % (lid, nem_addr))

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()
    
    logger.info("Closing lottery file")
    lottery_file.close()


if __name__ == '__main__':
    main()
