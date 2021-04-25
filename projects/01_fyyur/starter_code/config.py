import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# TODO (DONE) IMPLEMENT DATABASE URL
# Connected to a local db fyyurdb on postgres
SQLALCHEMY_DATABASE_URI = 'postgresql://piyush@127.0.0.1:5432/fyyurdb'
