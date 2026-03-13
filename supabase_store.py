# supabase_store.py
import uuid
import json
from db import supabase

LOCAL_SAVE_FILE = "fetched_resources.json"


def store_resources(resources):
    """
    Insert resources into Supabase without duplicates
    """

    if not resources:
        return

    new_resources = []

    for r in resources:

        try:
            # Check if resource already exists using URL
            existing = (
                supabase.table("resources")
                .select("url")
                .eq("url", r["url"])
                .execute()
            )

            if existing.data:
                print(f"⚠️ Duplicate skipped: {r['title']}")
                continue

            r["id"] = str(uuid.uuid4())
            new_resources.append(r)

        except Exception as e:
            print(f"Error checking duplicate for {r['title']}:", e)

    if not new_resources:
        print("No new resources to insert.")
        return

    # Save locally
    try:
        with open(LOCAL_SAVE_FILE, "a") as f:
            for r in new_resources:
                f.write(json.dumps(r) + "\n")
    except Exception as e:
        print("Error saving locally:", e)

    # Insert into Supabase
    try:
        supabase.table("resources").insert(new_resources).execute()
        print(f"✅ Inserted {len(new_resources)} new resources into Supabase.")
    except Exception as e:
        print("Error inserting into Supabase:", e)