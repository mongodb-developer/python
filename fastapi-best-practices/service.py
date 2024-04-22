from contextlib import asynccontextmanager
import os
import logging
from logging import info

from bson.json_util import dumps
from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient

# Load the MongoDB connection string from the environment variable MONGODB_URI
CONNECTION_STRING = os.environ["MONGODB_URI"]
PROFILES_COLLECTION = "profiles"


@asynccontextmanager
async def db_lifespan(app: FastAPI):
    """
    An async context manager, designed to be passed to FastAPI() as a lifespan.

    Initializes a MongoDB client and attaches it to the app as `mongodb_client`.
    Also attaches the default database as `database`,
    and the profiles collection as `profiles.

    On shutdown, ensures that the database connection is closed appropriately.
    """

    # Startup
    app.mongodb_client = AsyncIOMotorClient(CONNECTION_STRING)
    app.database = app.mongodb_client.get_default_database()
    app.profiles = app.database.get_collection(PROFILES_COLLECTION)
    ping_response = await app.database.command("ping")
    if int(ping_response["ok"]) != 1:
        raise Exception("Problem connecting to database cluster.")
    else:
        info("Connected to database cluster.")

    yield

    # Shutdown
    app.mongodb_client.close()


# Create an app - notice the lifespan that's defined above.
app: FastAPI = FastAPI(lifespan=db_lifespan)


@app.get("/people/{profile_id}")
async def read_item(profile_id: str):
    """
    Look up a single profile by ID.

    Try out "profile-12"!
    """
    # This API endpoint demonstrates using Motor directly to look up a single
    # profile by ID.
    profile = await app.profiles.find_one({"_id": profile_id})
    if profile is not None:
        return dumps(profile)
    else:
        raise HTTPException(
            status_code=404, detail=f"No profile with id '{profile_id}'"
        )


def main():
    """
    Run the app with uvicorn on port 8000.
    """

    try:
        import uvicorn

        logging.basicConfig(level=logging.INFO, format="%(levelname)s:     %(message)s")

        uvicorn.run("service:app", host="0.0.0.0", port=8000, reload=True)
    except KeyboardInterrupt:
        # Ignore keyboard interrupts.
        # They mean the user has (probably) hit Ctrl-C to shutdown the app.
        pass


if __name__ == "__main__":
    main()
