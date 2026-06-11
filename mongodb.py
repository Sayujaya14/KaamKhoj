from dotenv import load_dotenv
from pymongo import MongoClient
import os

load_dotenv()

# -------------------------
# Local MongoDB (Required)
# -------------------------

local_client = MongoClient(
    os.getenv("LOCAL_MONGO_URI", "mongodb://localhost:27017")
)

local_db = local_client["nepal_jobs"]
local_collection = local_db["jobs"]

local_collection.create_index(
    "url",
    unique=True
)

print("✅ Local MongoDB Connected")

# -------------------------
# Atlas MongoDB (Optional)
# -------------------------

atlas_collection = None

try:
    atlas_client = MongoClient(
        os.getenv("MONGO_URI"),
        serverSelectionTimeoutMS=5000
    )

    atlas_client.admin.command("ping")

    atlas_db = atlas_client["nepal_jobs"]

    atlas_collection = atlas_db["jobs"]

    atlas_collection.create_index(
        "url",
        unique=True
    )

    print("✅ Atlas Connected")

except Exception as e:
    print(f"⚠️ Atlas unavailable: {e}")


def save_jobs(jobs):

    local_inserted = 0
    local_updated = 0

    atlas_inserted = 0
    atlas_updated = 0

    for job in jobs:

        # -------------------------
        # Save to Local MongoDB
        # -------------------------

        result = local_collection.update_one(
            {"url": job["url"]},
            {"$set": job},
            upsert=True
        )

        if result.upserted_id:
            local_inserted += 1
        else:
            local_updated += 1

        # -------------------------
        # Save to Atlas (Optional)
        # -------------------------

        if atlas_collection:

            try:
                result = atlas_collection.update_one(
                    {"url": job["url"]},
                    {"$set": job},
                    upsert=True
                )

                if result.upserted_id:
                    atlas_inserted += 1
                else:
                    atlas_updated += 1

            except Exception as e:
                print(
                    f"Atlas save failed for {job['title']}: {e}"
                )

    print("\n======================")
    print("LOCAL MONGODB")
    print("======================")
    print(f"Inserted : {local_inserted}")
    print(f"Updated  : {local_updated}")

    if atlas_collection:

        print("\n======================")
        print("ATLAS")
        print("======================")
        print(f"Inserted : {atlas_inserted}")
        print(f"Updated  : {atlas_updated}")