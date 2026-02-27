print("MAIN FILE LOADED")

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from learning_path import generate_learning_path
from storage import save_learning_path
from learners import fetch_learner

app = FastAPI(
    title="AI Learning Path Generator",
    version="1.0"
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
def generate_path(request: GeneratePathRequest):
    user_id = request.user_id
    print("Received ID from frontend:", user_id)

    # 1️⃣ Fetch learner profile
    learner = fetch_learner(user_id)
    if not learner:
        raise HTTPException(status_code=404, detail="Learner not found")

    # 2️⃣ Generate roadmap (RAG + AI explanation)
    result = generate_learning_path(learner)  # Pass learner object directly

    if not result:
        raise HTTPException(status_code=500, detail="Failed to generate learning path")

    # 3️⃣ Save the generated roadmap in Supabase
    save_response = save_learning_path(
        learner_id=learner["id"],  # ✅ pass UUID string
        phases=result["phases"],
        explanation=result["explanation"],
        estimated_duration_weeks=result.get("estimated_duration_weeks"),
        success_probability=result.get("success_probability")
    )

    # 4️⃣ Return the result to the frontend
    return {
        "status": "success",
        "data": {
            "learner_id": user_id,
            "phases": result["phases"],
            "explanation": result["explanation"],
            "db_insert": "success" if save_response.data else "failed"
        }
    }