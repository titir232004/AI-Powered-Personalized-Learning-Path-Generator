from db import supabase


def save_learning_path(result):
    """
    Save generated learning path into Supabase.
    """

    response = supabase.table("learning_paths").insert({
        "learner_id": result["learner_id"],
        "phases": result["phases"],
        "estimated_duration_weeks": result["estimated_duration_weeks"],
        "success_probability": result["success_probability"],
        "explanation": result["explanation"]
    }).execute()

    return response