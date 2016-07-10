from flask import Flask
from moviecollection import database_setup as db_setup
from moviecollection.database_setup import User, Collection, Movie

app = Flask(__name__)

##############################################################################
# CSRF: for preventing cross-site request forgery
##############################################################################

# import moviecollection.views
# import moviecollection.api_JSON_ATOM
# import moviecollection.login


def start_session():
    """Gets a session (SQLAlchemy) with the database.

    Gets a new session with the testing or production database and assigns
    it to the global `session` variable. The session is also added as an
    attribute to 'app'. See `database_setup.py` for db_api type and db_tables.

    """
    app.session = db_setup.get_database_session()
# Access start_session method using a reference to app.
app.start_session = start_session


##############################################################################
# Helper functions for shorthand querying.
##############################################################################
def user():
    """Return a new query object for database User class."""
    return app.session.query(User)

app.User = user


def collection():
    """Return a new query object for database Collection class."""
    return app.session.query(Collection)

app.Collection = collection


def movie():
    """Return a new query object for database Movie class."""
    return app.session.query(Movie)

app.Movie = movie
