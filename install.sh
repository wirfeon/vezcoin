#!/bin/bash

#set -v

if [ "$#" -ne 2 ]; then
    echo "Illegal number of parameters"
    echo "Usage:"
    echo "./install \"service name\" \"path to install dir\""
    exit 1
fi

P=$2
S=$PWD
SERVICE_NAME=$1

rm -f /tmp/$SERVICE_NAME

[ ! -e $P ] && sudo mkdir -p $P

diff -q $P/bot.py bot.py > /dev/null 2>&1 || sudo cp bot.py $P/
diff -q $P/Pipfile Pipfile > /dev/null 2>&1 || (sudo cp Pipfile $P/ && echo 1 > /tmp/$SERVICE_NAME)

if [ ! -e $P/Pipfile.lock ]; then
    echo 1 > /tmp/$SERVICE_NAME
fi

if [ -e /tmp/$SERVICE_NAME ] && [ `cat /tmp/$SERVICE_NAME` == 1 ]; then
    cd $P
    sudo env PIPENV_VENV_IN_PROJECT=1 pipenv install --three
    sudo env PIPENV_VENV_IN_PROJECT=1 pipenv update
    cd $S
fi

rm -f /tmp/$SERVICE_NAME

if [ ! -e /etc/systemd/system/$SERVICE_NAME.service ]; then
    sudo cp service $P/
    sudo ln -sf $P/service /etc/systemd/system/$SERVICE_NAME.service 
else 
    diff -q $P/service service > /dev/null || (sudo cp service $P/ && sudo systemctl daemon-reload)
fi

if [ ! -e $P/data ]; then
    sudo mkdir $P/data
    sudo chown nobody $P/data
fi

sudo systemctl restart $SERVICE_NAME
sudo systemctl status $SERVICE_NAME
