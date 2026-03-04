def fetch_learner(user_id: str):
    response = supabase.table("learners") \
        .select("*") \
        .execute()

    print("ALL ROWS:", response.data)

    response_filtered = supabase.table("learners") \
        .select("*") \
        .eq("user_id", user_id) \
        .execute()

    print("FILTERED:", response_filtered.data)

    if not response_filtered.data:
        return None

    return response_filtered.data[0]
