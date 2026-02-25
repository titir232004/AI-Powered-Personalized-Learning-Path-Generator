from db import supabase

def fetch_learner(user_id: str):
    response = (
        supabase.table("learners")
        .select("*")
        .eq("user_id", user_id)
        .single()
        .execute()
    )

    return response.data