#!/bin/bash

sudo apt-get -y update
sudo apt-get -y install python3.6 python3-pip libgnutls28-dev libcurl4-openssl-dev libssl-dev unzip python3-dev build-essential jq
pip3 install setuptools

git clone https://github.com/dathbezumniy/kmd-sync-api.git
pip3 install -r kmd-sync-api/requirements.txt



