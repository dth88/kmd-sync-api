#!/usr/bin/env python3
import socket
import uvicorn
import logging
from lib import kmd_lib
from fastapi import FastAPI, Form

### API CALLS
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hi, I'm komodo sync api!"}


@app.get("/api_version")
async def api_version():
    return {"version": "0.0.1"}


@app.get("/sync_start/{ticker}")
async def chain_sync_stats(ticker: str = "ALL"):
    return kmd_lib.start_ticker(ticker)


@app.get("/sync_stop/{ticker}")
async def chain_sync_stats(ticker: str = "ALL"):
    return kmd_lib.stop_ticker(ticker)


@app.get("/sync_start_all")
async def start_sync_all():
    return kmd_lib.start_all_tickers()


@app.get("/sync_stop_all")
async def api_version():
    return kmd_lib.stop_all_tickers()


@app.get("/clean_folder/{ticker}")
async def chain_sync_stats(ticker: str = "ALL"):
    return kmd_lib.clean_ticker_data(ticker)


@app.get("/clean_assetchain_folders")
async def api_version():
    return kmd_lib.clean_all_ticker_data()


@app.get("/sync_stats_all")
async def start_sync_all():
    return kmd_lib.get_all_sync_stats()


@app.get("/tickers_params")
async def tickers_params():
    return kmd_lib.get_ticker_params()


@app.get("/tickers_list")
async def tickers_list():
    return kmd_lib.get_ticker_list()


@app.get("/upload_params")
async def upload_params(*, link : str = Form(...)):
    return kmd_lib.setup_params(link)


@app.post("/upload_binary")
async def upload_binary(*, link : str = Form(...)):
    return kmd_lib.setup_binary(link)


#deactivated issue #6
#@app.post("/upload_binary_dragndrop")
#async def upload_binary(*, link : str = Form(...)):
#    return kmd_lib.setup_binary_dragndrop(link)




#RPC CALLS TO SUPERVISOR

@app.post("/restart_api")
async def upload_binary(*, link : str = Form(...)):
    return kmd_lib.restart_api(link)


#deactivated issue #6
#@app.post("/download_zip")
#async def upload_binary(*, link : str = Form(...)):
#    return kmd_lib.restart_api(link)


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP



if __name__ == "__main__":
    ip = get_ip()
    uvicorn.run(app, host=ip, port=80)