#!/bin/bash

sudo apt-get -y update
sudo apt-get -y install python3.6 python3-pip

git clone https://github.com/dathbezumniy/kmd-sync-api.git
pip3 install -r kmd-sync-api/requirements.txt

mkdir .komodo
touch .komodo/komodo.conf
mkdir kmd-sync-api/logs

wget https://raw.githubusercontent.com/KomodoPlatform/komodo/master/zcutil/fetch-params.sh
chmod u+x fetch-params.sh
./fetch-params.sh


supervisord -c kmd-sync-api/supervisord.conf





