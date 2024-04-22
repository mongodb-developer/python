"""
Generate a JSON file containing some random sample data.

You shouldn't need to run this, because I've done it for you.
"""

from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path
import sys

from bson.json_util import dumps, CANONICAL_JSON_OPTIONS
from faker import Faker

OUTPUT_PATH = Path(__file__).parent / "../sample_data.json"


def generate_profile(f: Faker, uid: str):
    """Generate a user profile using Faker.

    The profile is generated with Faker,
    and then some of the datatypes are tidied up for exporting as JSON.
    """

    profile = f.profile()
    loc = profile["current_location"]
    profile["current_location"] = (float(loc[0]), float(loc[1]))
    profile["birthdate"] = datetime.combine(profile["birthdate"], datetime.min.time())
    profile["_id"] = uid

    return profile


def generate_sample_data(output_path: Path):
    """
    Generate a bunch of random user profiles, and save the data as extended JSON.
    """
    f = Faker()

    output_path.write_text(
        dumps(
            [generate_profile(f, f"profile-{i}") for i in range(1, 201)],
            json_options=CANONICAL_JSON_OPTIONS,
        )
    )


def main(argv=sys.argv[1:]):
    ap = ArgumentParser(description=__doc__)
    ap.add_argument("output_path", type=Path)

    args = ap.parse_args(argv)

    generate_sample_data(args.output_path)


if __name__ == "__main__":
    main()
