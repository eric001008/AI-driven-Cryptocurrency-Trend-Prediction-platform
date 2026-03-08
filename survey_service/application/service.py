from persistence import repository

SCORING_RULES = {
    # q1: What is your current level of experience in crypto investing?
    'q1': {'beginner': 5, 'intermediate': 10, 'advanced': 20},
    # q2: What is your primary objective when using this dashboard?
    'q2': {'monitor': 10, 'invest': 20, 'educate': 5, 'compliance': 15},
    # q3: What type of data do you find most useful?
    'q3': {'price': 20, 'sentiment': 10, 'aml': 5, 'macro': 15},
    # q4: How frequently do you trade or rebalance your portfolio?
    'q4': {'daily': 20, 'weekly': 15, 'monthly': 10, 'longterm': 5},
    # q5: Would you like to receive AML alerts when risk is detected?
    'q5': {'no': 10, 'yes': 5},
    # q6: What is your biggest challenge in analyzing crypto markets?
    'q6': {'tools': 20, 'timing': 15, 'understanding': 10, 'noise': 5}
}


def _calculate_rating(answers: list) -> dict:
    """
    A private helper function to calculate the total score and rating.
    """
    total_score = 0
    for ans in answers:
        question_id = ans.get('questionId')
        user_answer = ans.get('answer')

        # Look up the score for the given answer to the specific question
        score = SCORING_RULES.get(question_id, {}).get(user_answer, 0)
        total_score += score

    # Determine rating based on the total score
    if total_score <= 45:
        final_rating = 'C-Level - Conservative'
    elif 46 <= total_score <= 80:
        final_rating = 'B-Level - Balanced'
    else:  # total_score >= 81
        final_rating = 'A-Level - Aggressive'

    return {'score': total_score, 'rating': final_rating}


def process_and_save_survey(user_id: str, answers: list) -> dict:
    """
    The main service function that coordinates processing and saving the survey.
    """
    try:
        # 1. Calculate score and rating (this will now work)
        rating_info = _calculate_rating(answers)

        # 2. Create a map of answers with their calculated scores
        answers_with_scores_map = {}
        for item in answers:
            qid = item["questionId"]
            ans = item["answer"]
            score = SCORING_RULES.get(qid, {}).get(ans, 0)
            answers_with_scores_map[qid] = f"{ans} {score}"

        # 3. Call the repository to save the results
        success = repository.save_survey_results(user_id, answers_with_scores_map, rating_info)

        if not success:
            return {"status": "error", "message": "Could not save your survey results. Please try again later."}
        return {"status": "success", "rating_info": rating_info}

    except Exception as e:
        print(f"An unexpected error occurred while processing the survey: {e}")
        return {"status": "error", "message": "An internal error occurred while processing your request."}