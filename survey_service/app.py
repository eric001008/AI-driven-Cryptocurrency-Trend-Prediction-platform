from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

# 导入我们之前编写的应用层主服务函数
from application import service

app = FastAPI(
    title="Survey Rating Service",
    description="An internal microservice for processing user surveys and scoring them"
)

# -------------------- API Data Model (Data Contract) --------------------
# Use Pydantic models to define and validate the format of data received by the API.
# This ensures that the data passed to the business logic layer is clean and structured.
class SurveyAnswer(BaseModel):
    questionId: str
    answer: str

class SurveyPayload(BaseModel):
    userId: str
    answers: List[SurveyAnswer]

# -------------------- API Endpoints --------------------
@app.post("/initial_submit", response_model=Dict[str, Any])
def process_survey_endpoint(payload: SurveyPayload):
    print(f"--- The data to be verified finally received by Survey Service ---")
    print(payload.dict())
    print(f"---------------------------------------------")

    try:
        answers_dict = [ans.dict() for ans in payload.answers]
        result = service.process_and_save_survey(
            user_id=payload.userId,
            answers=answers_dict
        )

        # If the service layer returns an error, it also returns an error to the gateway
        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=result.get("message"))
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An internal error occurred while processing the request: {e}")

@app.get("/health", status_code=200)
def health_check():
    return {"status": "ok"}