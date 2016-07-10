from flask import jsonify, render_template
from moviecollection import app
from moviecollection.database_setup import Collection, Movie, User


##############################################################################
# JSON APIs to view Collection Information
##############################################################################
@app.route('/collection/JSON')
def collectionsJSON():
    """ Returns all collections in JSON format. """
    collections = app.Collection().all()
    return jsonify(Collections=[c.serialize for c in collections])


@app.route('/collection/<int:collection_id>/movie/JSON')
def collectionJSON(collection_id):
    """ Returns all movies of a distinct collection in JSON format.
    :param collection_id:
    """
    movies = app.Movie().filter_by(collection_id=collection_id).all()
    return jsonify(Movies=[a.serialize for a in movies])


@app.route('/collection/<int:collection_id>/movie/<int:movie_id>/JSON')
def movieJSON(collection_id, movie_id):
    """ Returns a distinct album in JSON format
    :param collection_id:

    Args:
        movie_id:
    """
    collection = app.Collection().filter_by(id=collection_id).one()
    movie = app.Movie().filter_by(id=movie_id).one()
    return jsonify(movie=movie.serialize, collection=collection.serialize)


##############################################################################
# ATOM APIs to view Collection Information
##############################################################################
@app.route('/collection/atom')
def collectionsATOM():
    """ Returns all collections in Atom format. """

    collections = app.Collection().all()
    return render_template('collections.xml', collections=collections)


@app.route('/collection/<int:collection_id>/movie/atom')
def collectionATOM(collection_id):
    """ Returns all albums of a distinct collection in Atom format. """

    collection = app.Collection().filter_by(id=collection_id).one()
    movies = app.Movie().filter_by(collection_id=collection_id).all()
    return render_template('movies.xml', movies=movies, collection=collection)


@app.route('/collection/<int:collection_id>/movie/<int:movie_id>/atom')
def movieATOM(collection_id, movie_id):
    """ Returns a distinct album in Atom format """

    collection = app.Collection().filter_by(id=collection_id).one()
    movie = app.Movie().filter_by(id=movie_id).one()
    return render_template('movie.xml', movie=movie, collection=collection)
