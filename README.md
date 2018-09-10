## Prerequisities

Installing python3, its package manager and virtual environment.

```
aptitude update
aptitude install python3 python3-pip 
sudo pip3 install --prefix /usr/local/ pipenv
```

## Installing

Get the source code
```
git clone git@github.com:wirfeon/vezcoin.git
```

Prepare the configuration
```
cp pricebot/service.template pricebot/service
```

Edit configuration in pricebot/service:
 * Environment=BOT_TOKEN - Bot token according to BotFather
 * Environment=WEB_HOOK - Web hook for Telegram API
 * Environment=PORT - Local port on which the bot will listen
 * Environment=CERTIFICATE - Path to .pem file of your bots certificate
 * WorkingDirectory - Install path of the bot

Run the install script
```./install.sh mycoinvest pricebot /www```

Parameters are respectively: 
 * group name
 * service name - must be one of the pricebot, bountybot, helperbot
 * install directory

The bot should be up and running now. You can check with
```systemctl status mycoinvest.pricebot.service```

Logs can be seen with
```journalctl -f -u mycoinvest.pricebot.service```
