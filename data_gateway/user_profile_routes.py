# data_gateway/user_profile_routes.py

from flask import Blueprint, request, jsonify
import psycopg2
import os
import jwt  # Ensure the jwt library is imported
from datetime import datetime

# 1. Create a new Blueprint
profile_bp = Blueprint('profile_api', __name__)


# 2. Helper functions for database connection and result formatting
def get_db_connection():
    """Establishes and returns a connection to the database."""
    return psycopg2.connect(
        host="db",
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )


def query_as_dict(cursor):

    cols = [desc[0] for desc in cursor.description]
    return [dict(zip(cols, row)) for row in cursor.fetchall()]


# 3. Get User Profile
@profile_bp.route('/profile', methods=['GET'])
def get_user_profile():
    """
    Fetches the complete profile for the authenticated user, including
    personal details, subscription plan, survey rating, and followed currencies.
    """
    auth_header = request.headers.get('Authorization')
    print("[DEBUG-profile] Authorization header received:", auth_header)
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"message": "Authentication Token is missing or has an incorrect format"}), 401

    token = auth_header.split(" ")[1]
    try:
        secret_key = os.getenv("SECRET_KEY")
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        user_id = payload['user_id']
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token has expired, please log in again"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "Token is invalid"}), 401

    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Query for main profile data by joining users, subscriptions, and survey results
        cur.execute("""
            SELECT
                u.username,
                u.email,
                s.name AS subscription_plan,
                s.max_currencies,
                sr.rating
            FROM
                ods.users u
            LEFT JOIN
                ods.subscriptions s ON u.subscription_id = s.subscription_id
            LEFT JOIN
                ods.survey_results sr ON u.user_id = sr.user_id
            WHERE
                u.user_id = %s;
        """, (user_id,))

        profile_data_list = query_as_dict(cur)
        if not profile_data_list:
            return jsonify({"message": "User not found"}), 404
        profile_data = profile_data_list[0]

        # Query for the user's followed currencies
        cur.execute("""
            SELECT c.symbol
            FROM ods.user_currencies uc
            JOIN ods.currencies c ON uc.currency_id = c.currency_id
            WHERE uc.user_id = %s;
        """, (user_id,))

        # Append the list of followed currencies to the main profile data
        currencies_list = query_as_dict(cur)
        profile_data['followed_currencies'] = [item['symbol'] for item in currencies_list]

        return jsonify(profile_data)

    except Exception as e:
        print(f"Error fetching user profile: {e}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        if conn:
            conn.close()


# 4. Update User's Preferred Currencies
@profile_bp.route('/preferences', methods=['POST'])
def update_user_preferences():
    """
    Updates the list of currencies a user is following.
    """
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"message": "Authentication Token is missing or has an incorrect format"}), 401

    token = auth_header.split(" ")[1]
    try:
        secret_key = os.getenv("SECRET_KEY")
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        user_id = payload['user_id']
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token has expired, please log in again"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "Token is invalid"}), 401

    data = request.get_json()
    symbols = data.get("symbols", [])

    if not isinstance(symbols, list):
        return jsonify({"message": "The 'symbols' parameter should be an array"}), 400

    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Get the corresponding currency_ids for the provided symbols
        cur.execute("SELECT symbol, currency_id FROM ods.currencies WHERE symbol = ANY(%s)", (symbols,))
        result = cur.fetchall()
        symbol_to_id = {symbol: cid for symbol, cid in result}

        # First, delete all existing currency preferences for this user
        cur.execute("DELETE FROM ods.user_currencies WHERE user_id = %s", (user_id,))

        # Then, insert the new preferences
        for symbol in symbols:
            if symbol in symbol_to_id:
                cur.execute("""
                    INSERT INTO ods.user_currencies (user_id, currency_id, added_at)
                    VALUES (%s, %s, %s)
                """, (user_id, symbol_to_id[symbol], datetime.utcnow()))

        conn.commit()
        return jsonify({"message": "User preferences updated successfully"})

    except Exception as e:
        print(f"Error updating preferences: {e}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        if conn:
            conn.close()