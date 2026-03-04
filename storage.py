from db import supabase
from datetime import datetime

def save_learning_path(
    learner_id: str,
    phases,
    explanation_basics=None,
    explanation_intermediate=None,
    explanation_advanced=None,
    explanation_outcomes=None,
    estimated_duration_weeks=None,
    success_probability=None
):
    if not learner_id:
        raise ValueError("learner_id must be a valid UUID string")

    # Ensure explanations are stored as JSONB
    def as_jsonb(value):
        if value is None:
            return None
        if isinstance(value, dict):
            return value
        return {"text": value}

    data_to_insert = {
        "learner_id": learner_id,
        "phases": phases,
        "estimated_duration_weeks": estimated_duration_weeks,
        "success_probability": success_probability,
        "explanation_basics": as_jsonb(explanation_basics),
        "explanation_intermediate": as_jsonb(explanation_intermediate),
        "explanation_advanced": as_jsonb(explanation_advanced),
        "explanation_outcomes": as_jsonb(explanation_outcomes),
        "created_at": datetime.utcnow().isoformat()
    }

    response = supabase.table("learning_paths").insert(data_to_insert).execute()

    if response.data:
        print("✅ Database insert successful")
    else:
        print("❌ Database insert failed:", response)

    return response
