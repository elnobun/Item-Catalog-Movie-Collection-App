import os
from sqlalchemy import asc
from werkzeug.utils import secure_filename
from moviecollection import app
from functools import wraps
from moviecollection.login import login_session
from flask import render_template, redirect, url_for, flash, request
from moviecollection.database_setup import User, Collection, Movie


##############################################################################
# User Helper funtion:
###############################################################################
def createUser(login_session):
    """ Creates a new user in the database.

    Args:
        login_session: session object with user data.

    Returns:
        user.id: generated distinct integer value identifying the newly created
            user.

    """

    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    app.session.add(newUser)
    app.session.commit()
    user = app.session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    """ Returns the user object associated with the given id number.

    Args:
        user_id: An integer identifying a distinct user.

    Returns:
        A user object containing all fields of the found row in the database.
    """

    user = app.session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    """ Return a user ID from the database.

    Returns a user id for a given e-mail address if the e-mail address belongs
    to a user stored in the database.

    Args:
        email: e-mail address of a user.

    Returns:
        If successful, the user id to the given e-mail address, otherwise
            nothing.
    """

    try:
        user = app.session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


##############################################################################
# Settings for the image upload functionality.
##############################################################################

# Dynamically determine the root directory.
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

# Folder for the uploaded album cover images.
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static/uploads')

# Allow only certain file extensions for uploaded images.
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Limit the file upload size to 2 megabytes.
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024


##############################################################################
# Render image upload
###############################################################################
def file_extension_allowed(filename):
    ''' Checks file for allowed extensions.

    Checks if file extension is in the predefined list of allowed extensions to
    make sure that users are not able to upload HTML files that would cause
    Cross-Site Scripting problems.
    :param filename:
    '''
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def image_source_process(image_source):
    """ Save image information to the database, depending on its source.

    Save image when local file is uploaded, save the path when url is
    given, otherwise just take the default image.

    This method is called from the editAlbum und deleteAlbum methods.

    Args:
        image_source: selected image_source in form.

    Returns:
        source: Local file, external url or no image.
        filename: Path or filename pointing to the image.

    """
    if image_source == 'local':
        source = 'local'
        # Access the image from the files dictionary on the request object.
        file = request.files['file']
        if file and file_extension_allowed(file.filename):
            # Validate filename in case it is forged.
            filename = secure_filename(file.filename)
            # Save the image in the defined upload folder on the server.
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    elif image_source == 'url':
        source = 'url'
        filename = request.form['URL']
    else:
        source = None
        filename = 'no_cover.png'
    return (source, filename)


##############################################################################
# Render template - These app.routes respond with web pages.
###############################################################################
## Collection
@app.route('/')
@app.route('/collection/')
def showCollections():
    "Shows all movie collection in the database"

    collections = app.Collection().order_by(asc(Collection.name))
    if 'username' not in login_session:
        return render_template('publicCollections.html', collections=collections)

    else:
        return render_template('showCollections.html', collections=collections)


@app.route('/collection/new', methods=['GET', 'POST'])
def newCollection():
    """Create new movie collection in the database

    Returns:
        on GET: Page to create a new collection.
        on POST: Redirect to main page after collection has been created.
        Login page when user is not signed in.
    """
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newCollection = Collection(name=request.form['name'], user_id=login_session['user_id'])
        app.session.add(newCollection)
        flash('New Collection %s Successfully Created' % newCollection.name)
        app.session.commit()
        return redirect(url_for('showCollections'))


    else:
        return render_template('newCollection.html')


@app.route('/collection/<int:collection_id>/edit/', methods=['GET', 'POST'])
def editCollection(collection_id):
    """ Edit a music collection in the database.

    Args:
        collection_id: An integer identifying a distinct collection.

    Returns:
        on GET: Page to edit a collection.
        on POST: Redirect to main page after collection has been edited.
        Login page when user is not signed in.
        Alert when user is trying to edit a collection he is not authorized to.
    """
    editedCollection = app.session.query(Collection).filter_by(id=collection_id).one()
    collection = app.session.query(Collection).filter_by(id=collection_id).one()
    creator = getUserInfo(collection.user_id)
    if 'username' not in login_session:
        return redirect('/login')
    if editedCollection.user_id != login_session['user_id']:
        return ("<script>function myFunction() {alert('You are not authorized "
                "to edit this collection. Please create your own collection in"
                " order to edit.');}</script><body onload='myFunction()'>")
    if request.method == 'POST':
        if request.form['name']:
            editedCollection.name = request.form['name']
            flash('Collection Successfully Edited: %s' % editedCollection.name)
            return redirect(url_for('showCollections'))
    else:
        return render_template('editCollection.html', collection=collection,
                               editcollection=editedCollection, creator=creator)


@app.route('/collection/<int:collection_id>/delete/', methods=['GET', 'POST'])
def deleteCollection(collection_id):
    """ Delete a music collection in the database.

    Args:
        collection_id: An integer identifying a distinct collection.

    Returns:
        on GET: Page to delete a collection.
        on POST: Redirect to main page after collection has been deleted.
        Login page when user is not signed in.
        Alert when user tries to delete a collection he is not authorized to.
    """
    collectionToDelete = app.session.query(Collection).filter_by(id=collection_id).one()
    collection = app.session.query(Collection).filter_by(id=collection_id).one()
    creator = getUserInfo(collection.user_id)
    if 'username' not in login_session:
        return redirect('/login')
    if collectionToDelete.user_id != login_session['user_id']:
        return ("<script>function myFunction() {alert('You are not authorized "
                "to delete this collection. Plaease create your own collection"
                " in order to delete.');}</script><body onload='myFunction()'"
                ">")
    if request.method == 'POST':
        app.session.delete(collectionToDelete)
        flash('%s Successfully Deleted' % collectionToDelete.name)
        app.session.commit()
        return redirect(url_for('showCollections', collection_id=collection_id))
    else:
        return render_template('deleteCollection.html', collection=collection,
                               collectionToDelete=collectionToDelete, creator=creator)


### Movie ####################################
@app.route('/collection/<int:collection_id>/')
@app.route('/collection/<int:collection_id>/movie/')
def showMovies(collection_id):
    """show all movies of a distinct collection
    Args:
        collection_id: An integer identifying a distinct collection.
    """
    collection = app.session.query(Collection).filter_by(id=collection_id).one()
    creator = getUserInfo(collection.user_id)
    movies = app.session.query(Movie).filter_by(
        collection_id=collection_id).all()
    if ('username' not in login_session or
                creator.id != login_session['user_id']):
        return render_template('publicMovies.html', movies=movies,
                               collection=collection, creator=creator)
    # The logged in user is the creator of the collection.
    else:
        return render_template('showMovies.html', movies=movies, collection=collection, creator=creator)


@app.route('/collection/<int:collection_id>/movie/new', methods=['GET', 'POST'])
def newMovie(collection_id):
    """ Create a new album in the database.

        Args:
            collection_id: An integer identifying a distinct collection.

        Returns:
            on GET: Page to create a new album.
            on POST: Redirect to collection page after album has been created.
            Login page when user is not signed in.
            Alert when user is trying to create an album he is not authorized to.
        """
    if 'username' not in login_session:
        return redirect('/login')
    collection = app.session.query(Collection).filter_by(id=collection_id).one()
    creator = getUserInfo(collection.user_id)
    if request.method == 'POST':
        source, filename = image_source_process(request.form['image_source'])
        newMovie = Movie(name=request.form['name'],
                         director=request.form['director'],
                         genre=request.form['genre'],
                         year=request.form['year'],
                         description=request.form['description'],
                         cover_source=source,
                         cover_image=filename,
                         collection_id=collection_id,
                         user_id=login_session['user_id'])
        app.session.add(newMovie)
        app.session.commit()
        flash('New movie: %s,  was Successfully Created' % newMovie.name)
        return redirect(url_for('showMovies', collection_id=collection_id))
    else:
        return render_template('newMovie.html', collection_id=collection_id, collection=collection,
                               creator=creator)


@app.route('/collection/<int:collection_id>/<int:movie_id>/edit', methods=['GET', 'POST'])
def editMovie(collection_id, movie_id):
    """ Edit an existing album in the database.

    Args:
        movie_id:
        collection_id: An integer identifying a distinct collection.
        album_id: An integer identifying a distinct album.

    Returns:
        on GET: Page to edit an album.
        on POST: Redirect to collection page after album has been edited.
        Login page when user is not signed in.
        Alert when user is trying to edit an album he is not authorized to.

    """
    if 'username' not in login_session:
        return redirect('/login')
    editedMovie = app.session.query(Movie).filter_by(id=movie_id).one()
    collection = app.session.query(Collection).filter_by(id=collection_id).one()
    creator = getUserInfo(collection.user_id)
    if login_session['user_id'] != collection.user_id:
        return ("<script>function myFunction() {alert('You are not authorized "
                "to edit movies to this collection. Please create your own"
                " collection in order to edit albums.');}</script><body "
                "onload='myFunction()'>")
    if request.method == 'POST':
        if request.form['name']:
            editedMovie.name = request.form['name']
        if request.form['director']:
            editedMovie.director = request.form['director']
        if request.form['genre']:
            editedMovie.genre = request.form['genre']
        if request.form['year']:
            editedMovie.year = request.form['year']
        if request.form['description']:
            editedMovie.description = request.form['description']
        if request.form['image_source'] != 'no_change':
            if editedMovie.cover_source == 'local':
                # Delete the old image from the server if it still exists.
                try:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'],
                                           editedMovie.cover_image))
                except OSError:
                    pass
            editedMovie.cover_source, editedMovie.cover_image = \
                image_source_process(request.form['image_source'])
        app.session.add(editedMovie)
        app.session.commit()
        flash('Movie Successfully Edited')
        return redirect(url_for('showMovies', collection_id=collection_id))
    else:
        return render_template('editMovie.html', collection_id=collection_id, movie_id=movie_id,
                               movie=editedMovie, creator=creator)


@app.route('/collection/<int:collection_id>/<int:movie_id>/delete', methods=['GET', 'POST'])
def deleteMovie(collection_id, movie_id):
    """ Delete an existing album in the database.

    Args:
        movie_id:
        collection_id: An integer identifying a distinct collection.

    Returns:
        on GET: Page to delete an album.
        on POST: Redirect to collection page after album has been deleted.
        Login page when user is not signed in.
        Alert when user is trying to delete an album he is not authorized to.

    """
    if 'username' not in login_session:
        return redirect('/login')
    collection = app.session.query(Collection).filter_by(id=collection_id).one()
    movieToDelete = app.session.query(Movie).filter_by(id=movie_id).one()
    creator = getUserInfo(collection.user_id)
    if login_session['user_id'] != collection.user_id:
        return ("<script>function myFunction() {alert('You are not authorized "
                "to delete movies to this collection. Please create your "
                "own collection in order to delete albums.');}</script><body "
                "onload='myFunction()'>")
    if request.method == 'POST':
        if movieToDelete.cover_source == 'local':
            # Delete the old image from the server if it still exists.
            try:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'],
                          movieToDelete.cover_image))
            except OSError:
                pass
        app.session.delete(movieToDelete)
        app.session.commit()
        flash('Movie Successfully Deleted')
        return redirect(url_for('showMovies', collection_id=collection_id))
    else:
        return render_template('deleteMovie.html', movie=movieToDelete,
                               collection=collection, creator=creator)
