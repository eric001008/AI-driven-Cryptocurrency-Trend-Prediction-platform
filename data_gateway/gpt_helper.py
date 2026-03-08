import os
from openai import OpenAI

# --- Client Initialization ---
# Load the API key from environment variables for security.
api_key = os.getenv("GPT_KEY")
# Create an instance of the OpenAI client.
client = OpenAI(api_key=api_key)


def generate_response(rating: str, forecast: str) -> str:
    """
    Generates a personalized investment suggestion using the OpenAI GPT model.
    """
    # Construct the user-facing part of the prompt.
    full_prompt = (
        "User Rating: {rating}\n"
        "Forecast: {forecast}".format(rating=rating, forecast=forecast)
    )

    try:
        # Make the API call to the OpenAI Chat Completions endpoint.
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {
                    # The system message sets the persona and rules for the AI model.
                    "role": "system",
                    "content": (
                        "You are an investment advisor. Based on the user's risk level and forecast situation, you need to provide suggestions. "
                        "Your response should be within 20 words. There are three types of user levels: \n\n"
                        "Grade A: Experienced / Aggressive; Grade B: Balanced / Growth-Oriented; Grade C: Novice / Conservative."
                    )
                },
                {
                    # The user message provides the specific data for this request.
                    "role": "user",
                    "content": full_prompt
                }
            ],
            temperature=0.7,
            max_tokens=100,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        # Extract the AI's message and format the final output string.
        return forecast + '\n' + "Based on your risk assessment:\n" + response.choices[0].message.content.strip()

    except Exception as e:
        return f" {e}"