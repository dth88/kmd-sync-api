#!/bin/bash

sudo apt-get -y update
sudo apt-get -y install python3.6 python3-pip

git clone https://github.com/dathbezumniy/kmd-sync-api.git
pip3 install -r kmd-sync-api/requirements.txt
mkdir .komodo
mkdir kmd-sync-api/logs
supervisord -c kmd-sync-api/supervisord.conf





