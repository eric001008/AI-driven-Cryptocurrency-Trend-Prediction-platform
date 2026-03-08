FROM python:3.10-slim

WORKDIR /app
COPY . /app

RUN pip install \
    flask \
    flask-cors \
    flask-mail \
    python-dotenv \
    psycopg2-binary \
    bcrypt \
    PyJWT

CMD ["python", "-u", "user.py"]
