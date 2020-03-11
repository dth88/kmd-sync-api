#!/usr/bin/env python3
from fastapi import FastAPI
import uvicorn
import time
import json
import sys
import os
import logging





### API CALLS
app = FastAPI()
@app.get("/")
async def root():
    return {"message": "Welcome to Sync Status API. See /docs for all methods"}

@app.get("/api_version")
async def api_version():
    return {"version": "0.0.2"}

@app.get("/show_hashtip_oracles")
async def show_hashtip_oracles():
    return {"version": "0.0.2"}

@app.get("/show_hashtips")
async def show_hashtips():
    return {"version": "0.0.2"}

@app.get("/show_sync_node_data")
async def show_sync_node_data():
    return {"version": "0.0.2"}

@app.get("/chains_monitored")
async def chains_monitored():
    return {"version": "0.0.2"}

@app.get("/node_sync_stats/{node_name}")
async def node_sync_stats(node_name: str = "ALL"):
    return {"version": "0.0.2"}

@app.get("/chain_sync_stats/{ticker}")
async def chain_sync_stats(ticker: str = "ALL"):
    return {"version": "0.0.2"}

if __name__ == "__main__":
    format = '%(asctime)s %(levelname)-8s %(message)s'
    uvicorn.run(app, host="127.0.0.1", port=8000)