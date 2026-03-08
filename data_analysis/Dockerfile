FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y bash

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY . /app

RUN chmod +x /app/run_loop.sh

CMD ["/bin/bash", "/app/run_loop.sh"]