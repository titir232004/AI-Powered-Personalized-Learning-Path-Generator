from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from learning_path import generate_learning_path
from storage import save_learning_path
from learners import fetch_learner
import os
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AI Learning Path Generator",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# Request Schema
# ----------------------------
class GeneratePathRequest(BaseModel):
    user_id: str  # Supabase UUID of the learner


# ----------------------------
# Generate Learning Path API
# ----------------------------
@app.post("/generate-path")
async def generate_path(request: GeneratePathRequest):
    user_id = request.user_id
    print("Received ID from frontend:", user_id)

    learner = fetch_learner(user_id)
    if not learner:
        raise HTTPException(status_code=404, detail="Learner not found")

    result = await generate_learning_path(learner)

    if not result:
        raise HTTPException(status_code=500, detail="Failed to generate learning path")

    # -----------------------------
    # 🔹 Debug: print full result
    # -----------------------------
    print("=== Generated Learning Path ===")
    import json
    print(json.dumps(result, indent=2))
    print("=== End of Learning Path ===")

    save_response = save_learning_path(
        learner_id=learner["id"],
        phases=result["phases"],
        explanation_basics=result.get("explanation_basics"),
        explanation_intermediate=result.get("explanation_intermediate"),
        explanation_advanced=result.get("explanation_advanced"),
        explanation_outcomes=result.get("explanation_outcomes"),
        estimated_duration_weeks=result.get("estimated_duration_weeks"),
        success_probability=result.get("success_probability")
    )

    return {
        "status": "success",
        "data": {
            "learner_id": user_id,
            "phases": result["phases"],
            "explanation_basics": result.get("explanation_basics"),
            "explanation_intermediate": result.get("explanation_intermediate"),
            "explanation_advanced": result.get("explanation_advanced"),
            "explanation_outcomes": result.get("explanation_outcomes"),
            "db_insert": "success" if save_response.data else "failed"
        }
    }









