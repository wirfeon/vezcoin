## Prerequisities

aptitude update
aptitude install python3 python3-pip 

sudo pip3 install --prefix /usr/local/ pipenv

## Installing

git clone git@github.com:wirfeon/vezcoin.git

cp pricebot/service.template pricebot/service

Edit runtime setting in pricebot/service:
 * Environment=BOT_TOKEN - Bot token according to BotFather
 * Environment=WEB_HOOK - Web hook for Telegram API
 * Environment=PORT - Local port on which the bot will listen
 * Environment=CERTIFICATE - Path to .pem file of your bots certificate
 * WorkingDirectory - Install path of the bot
