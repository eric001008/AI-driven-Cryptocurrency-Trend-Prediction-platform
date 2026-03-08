FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt /tmp/requirements.txt
RUN apt-get update && \
    apt-get install -y bash && \
    pip install --no-cache-dir -r /tmp/requirements.txt && \
    python -m textblob.download_corpora

COPY . /app

RUN chmod +x /app/run_pipeline.sh

CMD ["/bin/bash", "/app/run_pipeline.sh"]
