"""
Load a sample data JSON file into MongoDB.

You could use mongoimport for this, but this script removes the dependency,
and this defaults to using the same MONGODB_URI environment variable that the
FastAPI application uses.
"""

from argparse import ArgumentParser
import asyncio
from pathlib import Path
import os
import sys

from bson.json_util import loads, CANONICAL_JSON_OPTIONS
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


# Load the MongoDB connection string from the environment variable MONGODB_URI
CONNECTION_STRING = os.environ["MONGODB_URI"]
COLLECTION_NAME = "profiles"


async def check_database_connection(db: AsyncIOMotorDatabase):
    """Check connection to the database cluster."""

    ping_response = await db.command("ping")
    if int(ping_response["ok"]) != 1:
        raise Exception("Problem connecting to database cluster.")
    else:
        print("Connected to database cluster.")


async def load_sample_data(data_file: Path):
    """Connect to MongoDB and load in the sample data from the provided data_file."""
    sample_data = loads(data_file.read_text(), json_options=CANONICAL_JSON_OPTIONS)

    db = AsyncIOMotorClient(CONNECTION_STRING).get_default_database()
    collection = db.get_collection(COLLECTION_NAME)

    await check_database_connection(db)

    await collection.delete_many({})
    await collection.insert_many(sample_data)
    print(f"Loaded {len(sample_data)} profiles.")


async def main(argv=sys.argv[1:]):
    try:
        ap = ArgumentParser(description=__doc__)
        ap.add_argument("data_file", type=Path)

        args = ap.parse_args(argv)

        await load_sample_data(args.data_file)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    asyncio.run(main())
