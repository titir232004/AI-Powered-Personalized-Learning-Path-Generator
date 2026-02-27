from db import supabase


def fetch_learner(user_id: str):

    response = supabase.table("learners") \
        .select("*") \
        .eq("user_id",user_id) \
        .execute()

    if not response.data:
        return None

    return response.data[0]