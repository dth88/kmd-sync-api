#!/bin/bash

sudo apt-get -y update
sudo apt-get -y install python3.6
sudo apt-get -y install python3-pip
sudo apt-get -y install git
sudo apt-get -y install python3-dev
sudo apt-get -y install build-essential
sudo apt-get -y install libssl-dev
sudo apt-get -y install libcurl4-openssl-dev

pip3 install setuptools
pip3 install wheel
pip3 install slick-bitcoinrpc

git clone https://github.com/dathbezumniy/kmd-sync-api.git
pip3 install -r kmd-sync-api/requirements.txt

mkdir .komodo
touch .komodo/komodo.conf
echo rpcuser=myrpcusername >> .komodo/komodo.conf
echo rpcpassword=myrpcpassword >> .komodo/komodo.conf
mkdir komodo
touch komodo/komodod
touch komodo/komodo-cli
mkdir kmd-sync-api/logs
mkdir kmd-sync-api/ticker_output


export PATH=$PATH:/root/komodo
echo export PATH=$PATH:/root/komodo >> /root/.bashrc

supervisord -c kmd-sync-api/supervisord.conf


wget https://raw.githubusercontent.com/KomodoPlatform/komodo/master/zcutil/fetch-params.sh
chmod u+x fetch-params.sh
./fetch-params.sh








