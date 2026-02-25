from db import supabase


def fetch_latest_assessment(learner_id: str):

    print("\n=== ASSESSMENT DEBUG INFO ===")
    print("Querying for learner_id:", learner_id)

    response = supabase.table("assessment_results") \
        .select("*") \
        .eq("learner_id", learner_id) \
        .order("created_at", desc=True) \
        .limit(1) \
        .execute()

    print("Raw response:", response)
    print("Data returned:", response.data)
    print("=============================\n")

    if not response.data:
        return None

    return response.data[0]