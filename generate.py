import os

folders = {
    "data_acquisition": ["Dockerfile", "main.py"],
    "data_cleansing": ["Dockerfile", "main.py"],
    "data_update": ["Dockerfile", "app.py"],
    "frontend/src": ["App.js", "index.js"],
    "frontend/public": [],
    "db": ["init.sql"]
}

base_files = {
    ".env": "POSTGRES_USER=reddit\nPOSTGRES_PASSWORD=secret\nPOSTGRES_DB=sentimentdb\n",
    "docker-compose.yml": """version: '3.8'

services:
  db:
    image: postgres:13
    restart: always
    env_file:
      - .env
    volumes:
      - ./db/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"

  data_acquisition:
    build: ./data_acquisition
    depends_on:
      - db

  data_cleansing:
    build: ./data_cleansing
    depends_on:
      - db

  data_update:
    build: ./data_update
    ports:
      - "5000:5000"
    depends_on:
      - db

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - data_update
"""
}

for path, files in folders.items():
    os.makedirs(path, exist_ok=True)
    for file in files:
        with open(os.path.join(path, file), "w") as f:
            f.write("# " + file + "\n")

for file, content in base_files.items():
    with open(file, "w") as f:
        f.write(content)

print("The project structure is generated!")
