# FastAPI Best Practices

This is a very small project, demonstrating some best practices recommended for
building applications with FastAPI & MongoDB.

# Read the article!

This code was primarily written to support an article called
[Best Practices for FastAPI and MongoDB].
You should go and read that first!
Once you've done that, if you want to see many of the tips implemented together,
come back here and take a browse through [service.py](./service.py) if you're using Motor directly,
or [service-beanie.py](./service-beanie.py) if you're using an ODM like Beanie.

# Run the Project

Although the project has been primarily written to be _read_,
it is entirely possible to run it. This is how...

## Install dependencies

```shell
pip install -r requirements.txt
```

## Configure your MongoDB connection string

You'll need to set an environment variable, `MONGODB_URI` before you run anything.
You can do this directly in your shell or IDE, or you could use a tool like
[direnv], [envdir], or [honcho].

The connection string should be set to a URI pointing to your MongoDB cluster.
The connection string should include the *database* you want to connect to,
after the final "/" character.
For example:

```shell
export MONGODB_URI='mongodb+srv://username:password@host/TEST_DATABASE'
```

## Import some sample data

This project includes a small script to load some sample data into the cluster
you've configured above. You can run it like this:

```shell
$ python scripts/load_sample_data.py sample_data.json
```

Once you've loaded in the sample data, you're ready to start the sample app!

## Run the apps

There are two different apps, `service.py` that is written using Motor,
and `service-beanie.py` that uses the [Beanie] ODM.

Both apps implement a `main` function, so you can run them with the following shell commands:

```shell
# You only need to run ONE of these...

# Run the Motor app:
python service.py

# Run the Beanie app:
python service-beanie.py
```

If you navigate to http://localhost:8000/docs you should be able to explore the API from your browser.

# Contribute!

Do you have any recommendations for best practices for using FastAPI with MongoDB?
We'd love to hear it!
Raise an issue describing your opinion, and we can discuss it.

[direnv]: https://direnv.net/
[envdir]: https://envdir.readthedocs.io/en/latest/usage.html
[honcho]: https://honcho.readthedocs.io/en/latest/
[Beanie]: https://beanie-odm.dev/
[Best Practices for FastAPI and MongoDB]: https://example.net/