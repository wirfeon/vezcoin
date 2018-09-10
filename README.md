Here are 3 bots for MyCoinvest telegram group chat. They can bu run on any machine with Python3 installed but current installation manual is for debian/linux.

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
```
./install.sh mycoinvest pricebot /www
```

Parameters are respectively: 
 * group name
 * service name - must be one of the pricebot, bountybot, helperbot
 * install directory

The bot should be up and running now. You can check with
```
systemctl status mycoinvest.pricebot.service
```

Logs can be seen with
```
journalctl -f -u mycoinvest.pricebot.service
```
## HTTPS
Bots are configured to handle http only. You must strip SSL from your webhook via Nginx or something similar.

### Using Nginx
```
aptitude install nginx
```
Edit /etc/nginx/nginx.conf to proxy pass traffic from a webhook to your bot and restart Nginx.
```
location /674612326:AAFiPVe-ptiuTrEHH0NZKo-Z8D5fsZSBVH4 { 
  proxy_pass  http://127.0.0.1:9005/; 

  proxy_set_header Host $host;
  proxy_set_header X-Real-IP $remote_addr;
  proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  proxy_set_header X-Forwarded-Proto $scheme;
}
```

```
sudo systemctl restart nginx
```
