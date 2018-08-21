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
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

_port = int(os.environ["PORT"])
_webhook = os.environ["WEB_HOOK"]
_token = os.environ["BOT_TOKEN"]
_location = os.environ["URL_LOCATION"]
_certificate = os.environ["CERTIFICATE"]
_listen = "127.0.0.1"

xem_usd = 0

nemchange_tickers = {
    "CVZ": "coinvest:vezcoin"
}

def coingecko(coin):
    response = requests.get("https://api.coingecko.com/api/v3/coins/" + coin).text
    data = json.loads(response)

    return float(data["market_data"]["current_price"]["usd"])

def scraper(bot, job):
    global xem_usd

    logger.info("Scraping coingecko")
    xem_usd = coingecko("nem")
    logger.info("Done")

def nemchange(ticker):
    global xem_usd

    logger.info("Pulling data on '{:s}'".format(ticker))
 
    body = requests.get("https://nemchange.com//Exchange/actualOrders2/" + nemchange_tickers[ticker] + "/nem:xem")
    if (body.text == "{}"):
        logger.warn("Empty response")
        return
    #endif

    token = "<td id='ratio2_0'>"
    start = body.text.find(token)
    end = body.text.find("</td>", start)
    ratio = float(body.text[start + len(token) : end])

    bid = 1 / ratio

    return bid
        
def price(bot, update):

    chat_title = update.message.chat.title
    logger.info("Request from '%s' %d" % (chat_title, update.message.chat.id))
	
    ticker = "CVZ"
    bid = nemchange(ticker)
    
    update.message.chat.send_message("1 {:s} = {:.6f} XEM = ${:.7f}".format(ticker, bid, bid * xem_usd))

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

def main():
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

    dp.add_handler(CommandHandler("price", price))

    job = updater.job_queue
    job_sec = job.run_repeating(scraper, interval=10, first=0)

    # log all errors
    dp.add_error_handler(error)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    logger.info("Running")
    updater.idle()

    logger.info("Stoping updater") 
    updater.stop()
 
if __name__ == '__main__':
    main()
