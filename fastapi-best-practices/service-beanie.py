from contextlib import asynccontextmanager
from datetime import datetime
import logging
from logging import info
import os
from typing import List, Optional

from beanie import Document, init_beanie
from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import Field

# Load the MongoDB connection string from the environment variable MONGODB_URI
CONNECTION_STRING = os.environ["MONGODB_URI"]
PROFILES_COLLECTION = "profiles"


#   {
#     "job": "Nurse, learning disability",
#     "company": "Wood-Bartlett",
#     "ssn": "211-17-0186",
#     "residence": "83773 Nancy Port\nEast Coltonborough, MD 58656",
#     "current_location": [
#       { "$numberDouble": "-7.3013195" },
#       { "$numberDouble": "-4.274565" }
#     ],
#     "blood_group": "AB+",
#     "website": [
#       "http://www.lara.com/",
#       "http://cooley.biz/",
#       "http://lopez.org/"
#     ],
#     "username": "rossmichele",
#     "name": "Bridget Zavala",
#     "sex": "F",
#     "address": "114 Derek Trafficway\nLake Sarah, WI 86822",
#     "mail": "jonesbrenda@yahoo.com",
#     "birthdate": { "$date": { "$numberLong": "-1406592000000" } },
#     "_id": "profile-1"
#   },


class Profile(Document):
    id: Optional[str] = Field(default=None, description="MongoDB document ObjectID")
    username: str
    name: str
    address: str
    mail: str
    birthdate: datetime
    sex: str
    company: str
    job: str
    ssn: str
    residence: str
    current_location: List[float]
    blood_group: str
    website: List[str]

    class Settings:
        name = "profiles"


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

    await init_beanie(database=app.database, document_models=[Profile])

    yield

    # Shutdown
    app.mongodb_client.close()


# Create an app - notice the lifespan that's defined above.
app: FastAPI = FastAPI(lifespan=db_lifespan)


@app.get("/people/{profile_id}")
async def read_item(profile_id: str) -> Profile:
    """
    Look up a single profile by ID.

    Try out "profile-12"!
    """
    # This API endpoint demonstrates using Motor directly to look up a single
    # profile by ID.
    # profile = await app.profiles.find_one({"_id": profile_id})
    profile = await Profile.find_one(Profile.id == profile_id)
    if profile is not None:
        return profile
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

        logging.basicConfig(
            level=logging.DEBUG, format="%(levelname)s:     %(message)s"
        )

        uvicorn.run("service-beanie:app", host="0.0.0.0", port=8000, reload=True)
    except KeyboardInterrupt:
        # Ignore keyboard interrupts.
        # They mean the user has (probably) hit Ctrl-C to shutdown the app.
        pass


if __name__ == "__main__":
    main()
