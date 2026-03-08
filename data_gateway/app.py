from flask import Flask, jsonify
from flask_cors import CORS
from survey_routes import survey_bp
from auth_routes import auth_bp
from coin_data_routes import coin_data_bp
from user_profile_routes import profile_bp
import os
import psycopg2

app = Flask(__name__)

CORS(app,
     resources={r"/api/*": {"origins": "http://localhost:3000"}},
     supports_credentials=True
)

app.register_blueprint(survey_bp, url_prefix='/api/survey')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(coin_data_bp, url_prefix='/api/data')
app.register_blueprint(profile_bp, url_prefix='/api/user')


def get_connection():
    return psycopg2.connect(
        host="db",
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )

def query_as_dict(cursor):
    cols = [desc[0] for desc in cursor.description]
    return [dict(zip(cols, row)) for row in cursor.fetchall()]


# General health check
@app.route("/gateway/health")
def health_check():
    return jsonify({"status": "gateway_is_healthy"})


# Start Entry
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)