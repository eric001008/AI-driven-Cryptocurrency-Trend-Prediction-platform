from flask import Flask, jsonify, request
import psycopg2
import os
import sys
import bcrypt
import jwt
import datetime
import random
from flask_cors import CORS
from dotenv import load_dotenv
from flask_mail import Mail, Message
from datetime import datetime, timedelta

load_dotenv()

app = Flask(__name__)
if os.environ.get("FLASK_ENV") == "test":
    app.config["TESTING"] = True
CORS(app, origins="http://localhost:3000", supports_credentials=True)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

app.config.update(
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_PORT=int(os.getenv("MAIL_PORT")),
    MAIL_USE_TLS=os.getenv("MAIL_USE_TLS") == "True",
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_DEFAULT_SENDER=os.getenv("MAIL_DEFAULT_SENDER")
)

mail = Mail(app)


def get_connection():
    return psycopg2.connect(
        host="db",
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )


@app.route("/api/posts")
def get_posts():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT author, content, created_utc, sentiment, sentiment_score
        FROM dwd.sentiment
        ORDER BY created_utc DESC
        LIMIT 10
    """)
    data = cur.fetchall()
    cur.close()
    conn.close()

    outs = [
        {
            "author": author if author is not None else "Unknown",
            "content": content[:100] if content is not None else "--",
            "created_utc": created_utc.isoformat() if created_utc else None,
            "sentiment": sentiment if sentiment is not None else "N/A",
            "score": score if score is not None else 0
        }
        for author, content, created_utc, sentiment, score in data
    ]

    print("RETURN:", outs, file=sys.stderr)
    return jsonify(outs)


@app.route("/api/login", methods=["POST"])
def login():
    if request.method == "OPTIONS":
        return '', 200
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "Email and password are required."}), 400

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # 1. First, get user info and password hash based on email
            cur.execute("""
                SELECT u.user_id, u.password_hash, u.username, s.name
                FROM ods.users u
                JOIN ods.subscriptions s ON u.subscription_id = s.subscription_id
                WHERE u.email = %s
            """, (email,))
            result = cur.fetchone()

            if not result:
                return jsonify({"message": "User not found."}), 401

            user_id, password_hash, username, subscription_name = result

            if not bcrypt.checkpw(password.encode(), password_hash.encode()):
                return jsonify({"message": "Incorrect password."}), 401

            # 2. Check if the user has completed the survey
            cur.execute("SELECT EXISTS (SELECT 1 FROM ods.survey_results WHERE user_id = %s)", (user_id,))
            has_completed_survey = cur.fetchone()[0]

            # 3. Generate JWT Token
            token = jwt.encode(
                {
                    "user_id": user_id,
                    "subscription": subscription_name,
                    "exp": datetime.utcnow() + timedelta(hours=24)
                },
                app.config["SECRET_KEY"],
                algorithm="HS256"
            )

            # 4. In the response, add the has_completed_survey status
            return jsonify({
                "token": token,
                "message": "Login successful.",
                "user": {
                    "user_id": user_id,
                    "username": username,
                    "subscription": subscription_name,
                    "has_completed_survey": has_completed_survey  # Inform the frontend of the user's status
                }
            }), 200

    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({"message": "An error occurred during login."}), 500
    finally:
        if conn:
            conn.close()


@app.route("/api/currencies", methods=["GET"])
def get_currencies():
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify({"message": "Missing Authorization header"}), 401

    try:
        token = auth_header.split()[1]
        payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
        subscription = payload.get("subscription")  # 'Free', 'Pro', 'Enterprise'

        conn = get_connection()
        cur = conn.cursor()

        # Return different currencies based on subscription level
        if subscription == "Free":
            cur.execute("""
                SELECT currency_id, name, symbol
                FROM ods.currencies
                ORDER BY currency_id ASC
                LIMIT 3
            """)
        else:
            cur.execute("""
                SELECT currency_id, name, symbol
                FROM ods.currencies
                ORDER BY currency_id ASC
            """)

        rows = cur.fetchall()
        cur.close()
        conn.close()

        currencies = [
            {"id": row[0], "name": row[1], "symbol": row[2]}
            for row in rows
        ]
        return jsonify(currencies), 200

    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "Invalid token"}), 401
    except Exception as e:
        print(f"Error in /api/currencies: {e}", file=sys.stderr)
        return jsonify({"message": "Internal server error"}), 500


def validate_registration(data):
    errors = {}
    if not data.get("username") or len(data["username"]) < 3:
        errors["username"] = "Username must be at least 3 characters long."
    if not data.get("email") or "@" not in data["email"]:
        errors["email"] = "Please provide a valid email address."
    if not data.get("password") or len(data["password"]) < 6:
        errors["password"] = "Password must be at least 6 characters long."
    return errors


@app.route("/api/register", methods=["POST", "OPTIONS"])
def register():
    if request.method == "OPTIONS":
        return '', 200

    payload = request.get_json()
    errors = validate_registration(payload)
    if errors:
        return jsonify({"status": "error", "errors": errors}), 400

    username = payload["username"]
    email = payload["email"]
    password = payload["password"]
    plan_name = payload.get("plan", "Free")
    code = payload.get("code")

    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    conn = get_connection()
    try:
        cur = conn.cursor()

        # Verify the verification code
        cur.execute("SELECT code, expires_at FROM email_verification WHERE email = %s", (email,))
        row = cur.fetchone()
        if not row:
            return jsonify({"status": "error", "message": "Verification code not found or has been used."}), 400

        stored_code, expires_at = row
        if code != stored_code:
            return jsonify({"status": "error", "message": "Incorrect verification code."}), 400
        if datetime.utcnow() > expires_at:
            return jsonify({"status": "error", "message": "Verification code has expired."}), 400

        # Get the subscription_id
        cur.execute("SELECT subscription_id FROM ods.subscriptions WHERE name = %s", (plan_name,))
        row = cur.fetchone()
        if not row:
            return jsonify({"status": "error", "message": f"Invalid subscription plan: {plan_name}"}), 400
        subscription_id = row[0]

        # Insert the new user directly (no longer pre-checking for existence)
        cur.execute("""
            INSERT INTO ods.users (username, email, password_hash, created_at, subscription_id)
            VALUES (%s, %s, %s, NOW(), %s)
            RETURNING user_id, created_at
        """, (username, email, password_hash, subscription_id))
        user_id, created_at = cur.fetchone()

        # Delete the used verification code and commit
        cur.execute("DELETE FROM email_verification WHERE email = %s", (email,))
        conn.commit()

        cur.close()
        return jsonify({
            "status": "success",
            "user": {
                "user_id": user_id,
                "username": username,
                "email": email,
                "created_at": created_at.isoformat()
            }
        }), 201

    except psycopg2.IntegrityError as e:
        # If the database reports an error due to a UNIQUE constraint (e.g., duplicate email), it will be caught here.
        conn.rollback()
        return jsonify({"status": "error", "message": "Email or username already exists."}), 409
    except Exception as e:
        conn.rollback()
        print(f"--- [LOGIN_SERVICE] UNEXPECTED ERROR: {e} ---", file=sys.stderr)
        return jsonify({"status": "error", "message": "An unexpected server error occurred."}), 500
    finally:
        if conn:
            conn.close()


@app.route("/api/send-code", methods=["POST"])
def send_code():
    data = request.get_json()
    email = data.get("email")
    if not email:
        return jsonify({"message": "Email is required"}), 400

    code = str(random.randint(100000, 999999))
    expires_at = datetime.utcnow() + timedelta(minutes=10) # Extend the verification code validity period for testing purposes

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO email_verification (email, code, expires_at)
            VALUES (%s, %s, %s)
            ON CONFLICT (email) DO UPDATE SET code = EXCLUDED.code, expires_at = EXCLUDED.expires_at
        """, (email, code, expires_at))
        conn.commit()

        # --- Core change: Add a "backdoor" for test mode ---
        if os.getenv("ENV_MODE") == "test":
            # In a test environment, return the verification code directly in the response without sending an email
            print(f"--- [LOGIN_SERVICE] Running in TEST MODE. Verification code for {email} is {code}", file=sys.stderr)
            return jsonify({
                "message": "Verification code sent successfully (Test Mode)",
                "verification_code": code  # <-- This is the "backdoor" needed for the test script
            }), 200
        # --- End of change ---

        # In a production environment, send the email as usual
        msg = Message("Your Verification Code", recipients=[email])
        msg.body = f"Your verification code is: {code}"
        mail.send(msg)

        return jsonify({"message": "Verification code sent successfully"}), 200
    except Exception as e:
        print(f"Error sending code: {e}", file=sys.stderr)
        return jsonify({"message": "Internal server error"}), 500
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)