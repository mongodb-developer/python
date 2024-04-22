"""
A small FastAPI application demonstrating some best practices for using FastAPI with MongoDB.
"""

from contextlib import asynccontextmanager
from datetime import datetime
import os
import logging
from logging import info
from typing import Annotated, Any, List, Mapping, Optional

from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field

# Load the MongoDB connection string from the environment variable MONGODB_URI
CONNECTION_STRING = os.environ["MONGODB_URI"]
PROFILES_COLLECTION = "profiles"

EXAMPLE_PROFILE = {
    "_id": "profile-12",
    "job": "Research officer, trade union",
    "company": "Brown PLC",
    "ssn": "636-75-3518",
    "residence": "3409 Robinson Harbor\nNorth Monica, HI 17943",
    "current_location": [89.371661, -102.604933],
    "blood_group": "AB+",
    "website": ["http://carlson.com/", "https://www.dougherty.info/"],
    "username": "terry53",
    "name": "Whitney Davis",
    "sex": "F",
    "address": "3874 Brittany Rue Apt. 447\nWest Amber, AK 09494",
    "mail": "ztorres@hotmail.com",
    "birthdate": "1987-07-19T00:00:00",
}


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
app: FastAPI = FastAPI(
    lifespan=db_lifespan,
    title="Best Practices with FastAPI & Motor",
    description="""
This is a sample application that demonstrates some best practices when building an application with FastAPI and MongoDB, using Motor.

## Endpoints

This sample application only supports a single endpoint:

* **Get Profile**:  `/profiles/{profile_id}`
""",
)


class Profile(BaseModel):
    """
    A profile for a single user.

    Contains some useful information about a person.
    """

    id: Optional[str] = Field(
        default=None, description="MongoDB document ObjectID", alias="_id"
    )
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


@app.get(
    "/profiles/{profile_id}",
    response_model=Profile,
    responses={
        200: {
            "description": "Profile requested by ID",
            "content": {"application/json": {"example": EXAMPLE_PROFILE}},
        },
    },
)
async def get_profile(profile_id: str) -> Mapping[str, Any]:
    """
    Look up a single profile by ID.

    Try out "profile-12"!
    """
    # This API endpoint demonstrates using Motor directly to look up a single
    # profile by ID.
    #
    # It uses `response_model` (above) to tell FastAPI the schema of the data
    # being returned, but it returns a dict directly, so that conversion and
    # validation is done by FastAPI, meaning you don't have to copy values
    # manually into a Profile before returning it.
    profile = await app.profiles.find_one({"_id": profile_id})
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

        logging.basicConfig(level=logging.INFO, format="%(levelname)s:     %(message)s")

        uvicorn.run("service:app", host="0.0.0.0", port=8000, reload=True)
    except KeyboardInterrupt:
        # Ignore keyboard interrupts.
        # They mean the user has (probably) hit Ctrl-C to shutdown the app.
        pass


if __name__ == "__main__":
    main()
