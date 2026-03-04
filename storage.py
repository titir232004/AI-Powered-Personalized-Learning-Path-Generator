from db import supabase
from datetime import datetime

def save_learning_path(
    learner_id: str,
    phases,
    explanation_basics,
    explanation_intermediate,
    explanation_advanced,
    explanation_outcomes,
    estimated_duration_weeks=None,
    success_probability=None
):
    if not learner_id:
        raise ValueError("learner_id must be a valid UUID string")

    data_to_insert = {
        "learner_id": learner_id,
        "phases": phases,
        "explanation_basics": explanation_basics,
        "explanation_intermediate": explanation_intermediate,
        "explanation_advanced": explanation_advanced,
        "explanation_outcomes": explanation_outcomes,
        "estimated_duration_weeks": estimated_duration_weeks,
        "success_probability": success_probability,
        "created_at": datetime.utcnow().isoformat()
    }

    response = supabase.table("learning_paths").insert(data_to_insert).execute()

    if response.data:
        print("✅ Database insert successful")
    else:
        print("❌ Database insert failed:", response)

    return response
