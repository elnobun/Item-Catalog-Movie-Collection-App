import requests
import string
import random
import json
import httplib2
from flask import request, flash, jsonify, render_template, redirect, url_for, make_response
from flask import session as login_session
from flask_sqlalchemy import xrange
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
from flask_seasurf import SeaSurf
from moviecollection import app
from moviecollection.database_setup import User

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

    user = app.session.query(User).filter_by(email=email).one()

    if user:
        return user.id
    else:
        return None

##############################################################################
# CSRF: for preventing cross-site request forgery
##############################################################################

csrf = SeaSurf(app)

##############################################################################
# Declare client_id for Google and facebook authentification by referencing the
# client_secrets file.
##############################################################################
app_token = json.loads(
    open('g_client_secret.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Movie Collection App"

app_id = json.loads(
    open('fb_client_secret.json', 'r').read()) ['web']['app_id']

app_secret = json.loads(
    open('fb_client_secret.json', 'r').read())['web']['app_secret']

##############################################################################
# Google+ Sign in/out
##############################################################################
@app.route('/login')
def showLogin():
    """ Render the login page after a random state token is created.

    Creates a random anti-forgery state token with each GET request sent to
    localhost:5000/login before rendering the login page.

    Returns:
        The login page.
    """

    # Create a variable which will be 32 characters long and a mix of uppercase
    # letters and digits.

    state = ''.join(random.choice(
        string.ascii_uppercase + string.digits) for x in xrange(32))
    # Store the state token in the login_session object.
    login_session['state'] = state
    return render_template('login.html', STATE=state)

@csrf.exempt
@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        return jsonify(message = 'Invalid state parameter'), 401

    # Handles G+ third-party signin.
    code = request.data
    try:
        oauth_flow = flow_from_clientsecrets('g_client_secret.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        # Exchange code for credentials object with token
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        return jsonify(message='Failed to upgrade authorization code'), 401

    # Check that access token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={}'
           .format(access_token))
    result = requests.get(url).json()
    # Abort if error.
    if result.get('error') is not None:
        return jsonify(message=result.get('error')), 500

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        return jsonify(message="Token's user ID doesn't match login."), 401

    # Verify that the access token is valid for this app.
    if result['issued_to'] != app_token:
        return jsonify(message="Token's client ID does not match app's."), 401

    # Verify if user is already logged in.
    stored_credentials = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        return jsonify(status='ok',
                       message='Current user is already connected.',
                       username=login_session['username'],
                       picture=login_session['picture'])

    # Store the access token in the session for later use.
    login_session['provider'] = 'google'
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    data = requests.get(userinfo_url, params=params).json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # Get user id from database or add new user.
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += '" style = "width: 300px; height: 300px; border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;">'

    flash("you are now logged in as {}".format(login_session['username']))

    return output


@app.route('/gdisconnect')
def gdisconnect():
    """Handles G+ signout."""
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        login_session.clear()
        return jsonify(error='Current user not connected.'), 401

    url = ('https://accounts.google.com/o/oauth2/revoke?token={}'.format(access_token))
    result = requests.get(url)

    if result.status_code == 200:
        # Reset the user's sesson.
        login_session.clear()
        resp = jsonify(status='ok', message='Successfully disconnected.')
        resp.set_cookie('_csrf', '', expires=0)
        return resp
    else:
        # For whatever reason, the given token was invalid.
        return jsonify(error='Failed to revoke token for given user.'), 400


##############################################################################
# Facebook Sign in/out
##############################################################################
@csrf.exempt
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    """ Handles the Facebook sign-in process on the server side.

    Read the login flow step by step on
    https://developers.facebook.com/docs/facebook-login/login-flow-for-web/v2.2.

    Returns:
        When the sign-in was successful, a html response is sent to the client
        sendTokenToServer-function confirming the login. Otherwise, the
        following response is returned:
        401 Unauthorized: There is a mismatch between the sent and
            received state token.
    """
    # Similarily to the Google login, the value of the state token is verified
    # to protect against cross-site reference forgery attacks.
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Exchange client token for long-lived server-side token with GET
    # /oauth/access_token?grant_type=fb_exchange_token&client_id={app-id}
    # &client_secret={app-secret}&fb_exchange_token={short-lived-token}.
    access_token = request.data
    url = ("https://graph.facebook.com/oauth/access_token?grant_type="
           "fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token="
           "%s" % (app_id, app_secret, access_token))
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    # not used: userinfo_url = "https://graph.facebook.com/v2.2/me"

    # The long-lived token includes an expires-field that indicates how long
    # this token is valid. Longterm tokens can last up to two months.
    # Strip expire tag from access token since it is not needed to make API
    # calls.
    token = result.split("&")[0]

    # If the token works API calls should be possible like in the following.
    url = 'https://graph.facebook.com/v2.5/me?%s&fields=name,id,email'% token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    data = json.loads(result)
    # Populate the login session.
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # Facebook uses a separate API call to retrieve a profile picture. So this
    # call is made separetely. The login_session is then populated with the url
    # for the users profile picture.
    url = ('https://graph.facebook.com/v2.5/me/picture?%s&redirect=0&'
           'height=200&width=200' % token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['picture'] = data["data"]["url"]

    # Get user id from database or add new user.
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += '" style = "width: 300px; height: 300px; border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;">'

    flash("you are now logged in as {}".format(login_session['username']))

    return output

@csrf.exempt
@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    url = 'https://graph.facebook.com/%s/permissions' % facebook_id
    result = requests.get(url, 'DELETE').json()
    if result.status_code == 200:
        # Reset the user's sesson.
        login_session.clear()
        resp = jsonify(status='ok', message='Successfully disconnected.')
        resp.set_cookie('_csrf', '', expires=0)
        return resp
    else:
        # For whatever reason, the given token was invalid.
        return jsonify(error='Failed to revoke token for given user.'), 400



@app.route('/disconnect')
def disconnect():
    """ Deletes all user session values and redirect to the main page."""

    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            del login_session['gplus_id']
            del login_session['access_token']
        if login_session['provider'] == 'facebook':
            # not used: fbdisconnect()
            del login_session['facebook_id']
        # Reset the user's session.
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully logged out.")
        return redirect(url_for('showCollections'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCollections'))





