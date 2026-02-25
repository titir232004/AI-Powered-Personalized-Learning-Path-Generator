import json
from learning_path import generate_learning_path
from storage import save_learning_path   # 👈 NEW
from db import supabase


def get_all_users():
    response = supabase.table("learners").select("*").execute()

    print("\n=== SUPABASE DEBUG INFO ===")
    print("Raw response:", response)
    print("Data returned:", response.data)
    print("===========================\n")

    if not response.data:
        raise Exception("No users found in database. Check table name, project URL, or RLS policy.")

    sample_row = response.data[0]

    if "id" in sample_row:
        id_column = "id"
    elif "user_id" in sample_row:
        id_column = "user_id"
    elif "uuid" in sample_row:
        id_column = "uuid"
    else:
        raise Exception("No valid ID column found in learners table.")

    return [user[id_column] for user in response.data]


def main():
    print("\n=== AI Learning Path Generator (AUTO MODE) ===\n")

    try:
        user_ids = get_all_users()
        print(f"✅ Found {len(user_ids)} users.\n")

        for user_id in user_ids:
            print(f"🔹 Generating path for User: {user_id}")

            # 1️⃣ Generate learning path
            result = generate_learning_path(user_id)

            print("   ✅ Path generated successfully")

            # 2️⃣ Save to Supabase
            save_learning_path(result)
            print("   ☁️ Saved to Supabase")

            # 3️⃣ Save local backup
        print("🎉 All users processed successfully!")

    except Exception as e:
        print("\n❌ SYSTEM ERROR:")
        print(str(e))


if __name__ == "__main__":
    main()