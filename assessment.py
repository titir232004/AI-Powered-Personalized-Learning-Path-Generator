from db import supabase

def fetch_latest_assessment(learner_id: str):
    response = (
        supabase.table("assessment_results")
        .select("*")
        .eq("learner_id", learner_id)
        .order("attempt_number", desc=True)
        .limit(1)
        .execute()
    )

    if response.data:
        return response.data[0]
    return None