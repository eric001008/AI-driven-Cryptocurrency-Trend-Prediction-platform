FROM python:3.10-slim

RUN apt-get update && \
    apt-get install -y bash && \
    pip install praw psycopg2-binary python-dotenv pandas telethon web3

WORKDIR /app
COPY . /app
# Make sure the script has execute permissions
RUN chmod +x /app/run_loop.sh

CMD ["/bin/bash", "/app/run_loop.sh"]
