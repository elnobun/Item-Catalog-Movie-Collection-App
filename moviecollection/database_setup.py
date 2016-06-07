import os
from sqlalchemy import Column as Col, ForeignKey, Integer, String as Str
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine


Base = declarative_base()

###############################################################################
# Tables: User, Collection, Album
###############################################################################

class User(Base):
    __tablename__ = 'user'
    """ Table for user information.

    Columns:
        id: Distinct user id.
        name: Name of the user.
        email: E-Mail of the user.
        picture: Path to external profile picture.
    """
    id = Col(Integer, primary_key=True)
    name = Col(Str(250), nullable=False)
    email = Col(Str(250), nullable=False)
    picture = Col(Str(250))

    @property
    def serialize(self):

        return {
            'name': self.name,
            'id': self.id,
            'email': self.email,
            'picture': self.picture,
        }


class Collection(Base):
    __tablename__ = 'collection'
    """ Table for movie collections.

    Columns:
        id: Distinct collection id.
        name: Name of the collection.
        user_id: user who created the collection.
    """

    id = Col(Integer, primary_key=True)
    name = Col(Str(250), nullable=False)
    user_id = Col(Integer, ForeignKey('user.id'))
    user = relationship(User)

    # Decorator method
    @property
    def serialize(self):
        """ Selects and formats collection data.

        This serializable function will help define what data should be
        sent across and put it in a format that Flask can easily use.
        """
        # Returns object data in easily serializeable format
        return {
            'id': self.id,
            'name': self.name
        }

class Movie(Base):
    __tablename__ = 'movie'
    """ Table for movie information.

    Columns:
        id: Distinct album id.
        name: Movie title.
        genre: Movie genre.
        year: Year in which the movie got published.
        description: Additional movie information.
        cover_source: Source of the optional movie cover image.
        cover_image: filename or external path to the optional album cover image.
        user_id: user who created the movie entry.
        collection_id: collections where the movie belongs to.
    """

    id = Col(Integer, primary_key=True)
    name = Col(Str(250), nullable=False)
    director = Col(Str(250), nullable=False)
    genre = Col(Str(100), nullable=False)
    year = Col(Str(4))
    description = Col(Str(250))
    cover_source = Col(Str(5))
    cover_image = Col(Str(250))
    user_id = Col(Integer, ForeignKey('user.id'))
    user = relationship(User)
    collection_id = Col(Integer, ForeignKey('collection.id'))
    collection = relationship(Collection)

    # Decorator method
    @property
    def serialize(self):
        """ Selects and formats album data.

        This serializable function will help define what data should be
        send across and put it in a format that Flask can easily use.
        """

        # Returns object data in easily serializable format
        return {
            'id': self.id,
            'name': self.name,
            'director': self.director,
            'genre': self.director,
            'year': self.year,
            'description': self.description
        }


###############################################################################
# Functions
###############################################################################
# Global variables for database API and database names - in this case, SQlite.
sqlite_dbapi = 'sqlite:///'
database_name = 'moviecollections.db'

use_SQlite = True  # Boolean

def get_database_session():
    """Returns a session for executing queries.

    Connects to a database, creates an engine and returns a session connection
    to the engine.

    :returns: A SQLAlchemy Session instance.
    """
    global engine
    db_name = database_name
    if use_SQlite:
        engine = create_engine(sqlite_dbapi + db_name)
        Base.metadata.bind = engine
    return sessionmaker(bind=engine)()


def create_all():
    """Adds tables defined above to the database.

    Deletes the database if it already exists and creates a new database in
    its place. The tables are defined in file as classes that inherit a
    ``declarative_base()`` instance.
    :param echo:
    """

    db_name = database_name

    if use_SQlite:
        engine = create_engine(sqlite_dbapi + db_name)
        Base.metadata.create_all(engine)

def drop_all():
    """Deletes all tables from database.
    """
    db_name = database_name
    if use_SQlite:
        engine = create_engine(sqlite_dbapi + db_name)
        Base.metadata.drop_all(engine)


def create_database():
    """Creates a new empty database.

    Deletes the database if it already exists and creates a new database in
    its place.
    """

    db_name = database_name

    try:
        os.remove(db_name)
    except OSError:
        pass
    create_engine(sqlite_dbapi + db_name)


if __name__ == '__main__':
    create_database()
    create_all()
