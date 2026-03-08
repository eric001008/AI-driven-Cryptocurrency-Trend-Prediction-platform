FROM python:3.10-slim

WORKDIR /app
COPY . /app

RUN pip install psycopg2-binary pandas
RUN pip install --no-cache-dir bcrypt


# --- Use the most direct startup command with unbuffered output ---
CMD ["python", "-u", "seed.py"]