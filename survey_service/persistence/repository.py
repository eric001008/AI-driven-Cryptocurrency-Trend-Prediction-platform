import psycopg2
import os

def get_db_connection():
    """
    Establishes and returns a connection to a database.
    """
    try:
        conn = psycopg2.connect(
            host="db",
            dbname=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD")
        )
        return conn
    except psycopg2.OperationalError as e:
        print(f"Database connection failed: {e}")
        raise


def save_survey_results(user_id: str, answers_map_with_scores: dict, rating_info: dict):
    """
    Insert the user's complete survey results (score and concatenated score answers)
    as a single row into the survey_results table.
    """
    sql = """
        INSERT INTO ods.survey_results (
            user_id, score, rating,
            answer_q1, answer_q2, answer_q3, answer_q4, answer_q5, answer_q6,
            created_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        ON CONFLICT (user_id) DO UPDATE SET
            score = EXCLUDED.score,
            rating = EXCLUDED.rating,
            answer_q1 = EXCLUDED.answer_q1,
            answer_q2 = EXCLUDED.answer_q2,
            answer_q3 = EXCLUDED.answer_q3,
            answer_q4 = EXCLUDED.answer_q4,
            answer_q5 = EXCLUDED.answer_q5,
            answer_q6 = EXCLUDED.answer_q6,
            created_at = NOW();
    """

    data_tuple = (
        int(user_id),
        rating_info['score'],
        rating_info['rating'],
        answers_map_with_scores.get('q1'),
        answers_map_with_scores.get('q2'),
        answers_map_with_scores.get('q3'),
        answers_map_with_scores.get('q4'),
        answers_map_with_scores.get('q5'),
        answers_map_with_scores.get('q6')
    )

    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute(sql, data_tuple)
        conn.commit()
        print(f"Successfully saved or updated the complete questionnaire result with score for user {user_id}.")
        return True
    except Exception as error:
        print(f"Database operation failed: {error}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()