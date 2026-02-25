from db import supabase


def fetch_learner(learner_id: str):

    response = supabase.table("learners") \
        .select("*") \
        .eq("id", learner_id) \
        .execute()

    if not response.data:
        return None

    return response.data[0]