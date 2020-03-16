#!/usr/bin/env python3
from fastapi import FastAPI
import uvicorn
import time
import json
import sys
import os
import logging
from lib import kmd_lib


### API CALLS
app = FastAPI()
@app.get("/")
async def root():
    return {"message": "Welcome to Sync Status API. See /docs for all methods"}


@app.get("/api_version")
async def api_version():
    return {"version": "0.0.2"}


@app.get("/ticker_sync_stats/{ticker}")
async def ticker_sync_stats(ticker: str = "ALL"):
    return {"version": "0.0.2"}


@app.get("/all_sync_stats/")
async def ticker_sync_stats():
    return {"version": "0.0.2"}


@app.get("/start_sync/{ticker}")
async def chain_sync_stats(ticker: str = "ALL"):
    return kmd_lib.start_ticker(ticker)


@app.get("/stop_sync/{ticker}")
async def chain_sync_stats(ticker: str = "ALL"):
    return kmd_lib.stop_ticker(ticker)


@app.get("/start_sync_all/")
async def start_sync_all():
    return kmd_lib.start_all_tickers()


@app.get("/stop_sync_all")
async def api_version():
    return kmd_lib.stop_all_tickers()









if __name__ == "__main__":
    format = '%(asctime)s %(levelname)-8s %(message)s'
    uvicorn.run(app, host="95.217.134.179", port=80)