from dotenv import load_dotenv
import os

from pymongo import MongoClient

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))

db = client["nepal_jobs"]

jobs_collection = db["jobs"]

# Prevent duplicate URLs
jobs_collection.create_index("url", unique=True)


def save_jobs(jobs):
    inserted = 0
    updated = 0

    for job in jobs:
        result = jobs_collection.update_one(
            {"url": job["url"]},
            {"$set": job},
            upsert=True
        )

        if result.upserted_id:
            inserted += 1
        else:
            updated += 1

    print(f"Inserted: {inserted}")
    print(f"Updated: {updated}")