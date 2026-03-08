import jwt
from flask import Blueprint, request, jsonify
import psycopg2

import os
from gpt_helper import generate_response

# from flask_cors import CORS
# app = Flask(__name__)
# CORS(app, supports_credentials=True)
coin_data_bp = Blueprint('coin_data_api', __name__)


# ========== Public utility functions ==========

def get_db_connection():
    return psycopg2.connect(
        host="db",
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        port=5432
    )


def query_as_dict(cursor):
    cols = [desc[0] for desc in cursor.description]
    return [dict(zip(cols, row)) for row in cursor.fetchall()]


def get_user_id_from_auth_header(auth_header) -> int:
    if not auth_header or not auth_header.startswith('Bearer '):
        raise ValueError("Authorization token is missing or malformed")

    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=["HS256"])
        print("USER ID:", payload['user_id'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")


def get_user_rating_by_id(user_id: int) -> float:
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT rating FROM ods.survey_results WHERE user_id = %s", (user_id,))
            row = cur.fetchone()
            if row is None:
                raise LookupError("User rating not found")
            return row[0]
    finally:
        if conn:
            conn.close()


@coin_data_bp.route('/coin_data')
def get_coin_data():
    symbol = request.args.get('symbol')
    if not symbol:
        return jsonify({"error": "symbol is required"}), 400

    auth_header = request.headers.get('Authorization')
    print("[DEBUG-coindata] Authorization header received:", auth_header)
    conn = None

    try:
        print("[DEBUG fetching] Fetching data from dws")
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT price, last_updated FROM dws.price_tb
            WHERE symbol = %s ORDER BY last_updated ASC
        """, (symbol.lower(),))
        price_trend = query_as_dict(cur)

        cur.execute("""
            SELECT * FROM dws.statistic_tb
            WHERE symbol = %s ORDER BY last_updated DESC LIMIT 1
        """, (symbol,))
        statistic_list = query_as_dict(cur)
        statistic = statistic_list[0] if statistic_list else {}

        cur.execute("""
            SELECT title, sentiment, sentiment_score, url FROM dws.content_sa_tb
            WHERE symbol = %s ORDER BY sentiment_score DESC LIMIT 5
        """, (symbol.lower(),))
        sentiment = query_as_dict(cur)

        cur.execute("""
            SELECT symbol, aml_label
            FROM dws.aml_predictions
            WHERE symbol = %s and aml_label = 1
        """, (symbol,))
        print('[DEBUG gateway AML]', cur)
        aml = query_as_dict(cur)

        cur.execute("""
            SELECT * FROM dws.latest_news
            WHERE symbol = %s LIMIT 6
        """, (symbol.lower(),))
        news = query_as_dict(cur)
        print('[DEBUG gateway]', news[:2])

        # Predict trends
        cur.execute("""
            SELECT trend FROM dws.predict_res
            WHERE symbol = %s LIMIT 1
        """, (symbol.lower(),))
        trend_row = cur.fetchone()
        trend = trend_row[0] if trend_row else "Data Deficiencies!"

        # Personalized recommendations
        recommendation = None
        try:
            if trend:
                print("GET TREND!", trend)
                user_id = get_user_id_from_auth_header(auth_header)
                rating = get_user_rating_by_id(user_id)
                print(rating)
                message = generate_response(rating=rating, forecast=trend)
                print('[DEBUG-recommend]: ', message)
                recommendation = {"message": message, "symbol": symbol}
        except Exception as e:
            print(f"[Recommendation Error] {e}")
            recommendation = None

        # Summarize the results
        return jsonify({
            "symbol": symbol,
            "price_trend": price_trend,
            "statistic": statistic,
            "sentiment": sentiment,
            "aml": aml,
            "news": news,
            "trend": trend,
            "recommendation": recommendation
        })

    except Exception as e:
        print(f"[Server Error] Error fetching coin data: {e}")
        return jsonify({"error": "An internal error occurred"}), 500
    finally:
        if conn:
            conn.close()
