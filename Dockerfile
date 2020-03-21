FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

RUN pip install slick-bitcoinrpc

COPY ./app /app