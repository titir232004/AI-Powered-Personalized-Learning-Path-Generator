from db import supabase
from datetime import datetime

def save_learning_path(learner_id: str, phases, explanation, estimated_duration_weeks=None, success_probability=None):
    """
    Save learning path to Supabase.
    learner_id: string UUID of the learner
    """
    if not learner_id:
        raise ValueError("learner_id must be a valid UUID string")

    data_to_insert = {
        "learner_id": learner_id,  # ✅ already UUID
        "phases": phases,
        "estimated_duration_weeks": estimated_duration_weeks,
        "success_probability": success_probability,
        "explanation": explanation,
        "created_at": datetime.utcnow().isoformat()
    }

    response = supabase.table("learning_paths").insert(data_to_insert).execute()

    if response.data:
        print("   ✅ Database insert successful")
    else:
        print("   ❌ Database insert failed:", response)

    return response