#!/bin/bash

#set -v

if [ "$#" -ne 3 ]; then
    echo "Illegal number of parameters"
    echo "Usage:"
    echo "./install \"group name\" \"service name\" \"path to install dir\""
    exit 1
fi

G=$1
S=$2
P=$3
SRC=$PWD

INSTALL=$P/$G/$S

rm -f /tmp/$G.$S

[ ! -e $INSTALL ] && sudo mkdir -p $INSTALL

diff -q $INSTALL/bot.py $S/bot.py > /dev/null 2>&1 || sudo cp $S/bot.py $INSTALL/
diff -q $INSTALL/Pipfile $S/Pipfile > /dev/null 2>&1 || (sudo cp $S/Pipfile $INSTALL/ && echo 1 > /tmp/$G.$S)

if [ ! -e $INSTALL/Pipfile.lock ]; then
    echo 1 > /tmp/$G.$S
fi

if [ -e /tmp/$G.$S ] && [ `cat /tmp/$G.$S` == 1 ]; then
    cd $INSTALL
    sudo env PIPENV_VENV_IN_PROJECT=1 pipenv install --three
    sudo env PIPENV_VENV_IN_PROJECT=1 pipenv update
    cd $SRC
fi

rm -f /tmp/$G.$S

if [ ! -e /etc/systemd/system/$G.$S.service ]; then
    sudo cp $S/service $INSTALL/
    sudo ln -sf $INSTALL/service /etc/systemd/system/$G.$S.service 
else 
    diff -q $INSTALL/service $S/service > /dev/null || (sudo cp $S/service $INSTALL/ && sudo systemctl daemon-reload)
fi

if [ ! -e $INSTALL/data ]; then
    sudo mkdir $INSTALL/data
    sudo chown $G $INSTALL/data
fi

sudo systemctl restart $G.$S.service
sudo systemctl status $G.$S.service
