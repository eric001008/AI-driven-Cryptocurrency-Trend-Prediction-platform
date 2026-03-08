FROM python:3.10-slim

WORKDIR /app
COPY . /app

RUN pip install flask psycopg2-binary flask-cors requests bcrypt PyJWT openai

EXPOSE 5000

# --- Use the most direct startup command with unbuffered output ---
CMD ["python", "-u", "app.py"]