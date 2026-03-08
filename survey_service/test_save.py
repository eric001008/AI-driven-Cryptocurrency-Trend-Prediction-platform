from application import service
import os

os.environ['POSTGRES_DB'] = 'overdb'
os.environ['POSTGRES_USER'] = 'admincedric'
os.environ['POSTGRES_PASSWORD'] = 'comp9900'


def run_database_test():
    """
    This function will independently test the core data processing and saving functions of the backend.
    """
    print("--- Start backend database saving test---")

    # 1. Forge a piece of data that will be sent by the front end and make up a user ID
    test_user_id = "backend-test-user-003"
    test_answers = [
        {"questionId": "q1", "answer": "1"},  # 20 marks
        {"questionId": "q_risk", "answer": "A"},  # 5 marks
        {"questionId": "q12", "answer": "1~2种"}  # 10 marks
    ]

    print(f"Test User ID: {test_user_id}")
    print(f"Test Questionnaire Answers: {test_answers}")

    # 2. Directly call our core service function, which will trigger calculation and database saving
    result = service.process_and_save_survey(
        user_id=test_user_id,
        answers=test_answers
    )

    # 3. Print the final result returned by the service function
    print(f"The service processing is completed and the result is returned: {result}")
    print("--- End of test ---")
    print("\nPlease go to your database management tool now and check whether the data has been successfully written into the survey.user_ratings and survey.survey_answers tables.")


if __name__ == "__main__":
    run_database_test()