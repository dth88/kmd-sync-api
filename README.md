# Komodo sync-api utility

## TL;DR

This sync-API deploys automatically via telegram kmd-sync-bot --> https://github.com/dathbezumniy/kmd-sync-bot

## Preface
This api and telegram kmd-sync-bot are in the very early development stages, so there's basically no security at all, anyone who knows your sync-api server ip address can call endpoints just as bot does. If you need any guidance on how to add features/configure or you want to propose an improvement please do not hesitate to contact me on komodo discord @dth.

For now both bot and api tested only on: Ubuntu 18.04 LTS bionic


## Installation

If for some unknown to me reason you would like to install this API without the help of our utility telegram bot then there's a simple .sh script that you can use.

```sh
"wget https://raw.githubusercontent.com/dathbezumniy/kmd-sync-api/master/sync_api_setup.sh && chmod u+x sync_api_setup.sh && ./sync_api_setup.sh"
```


## Manual routine if something goes wrong:
Check if supervisord and sync-api started properly:
```sh 
ps aux | grep python 
```
If you do not see sync-api.py running then you should check supervisord or api error log:

```sh
cat logs/sync-api.err.log
cat logs/supervisord.log
```

If you fixed the problem then start api again with:

```sh
supervisorctl start sync-api
supervisorctl stop sync-api
supervisorctl restart sync-api
```

If you cant figure the problem out, do not hesitate to paste this error message to me @dth on discord komodo channel or simply open up an issue here.


## Using sync-API

After successful installation, you will be able to call these api-endpoints:
```
GET:
/                          - {"message":"Hi, I'm komodo sync api!"}
/api_version               - {"version":"0.0.1"}
/sync_start/{ticker}       - Start individually
/sync_stop/{ticker}        - Stop individually
/sync_start_all            - Start all ACs
/sync_stop_all             - Stop all ACs
/clean_folder/{ticker}     - Clean sync-progress of individual AC
/clean_assetchain_folders  - Clean sync-progress of all ACs
/sync_stats_all            - Get dict of currently syncing chains.
/tickers_params            - Get dict of ACs launch params
/tickers_list              - Get list of ACs available for launch

POST:
/upload_params             - upload custom launch params for ACs
/upload_binary             - upload custom komodod binary
/restart_api               - restart api
```
