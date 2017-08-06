from facebook import get_user_from_cookie, GraphAPI, GraphAPIError
from flask import g, render_template, redirect, request, session, url_for
from flask_login import login_user, logout_user, login_required

from app import app, db, login_manager
from .models import User

FB_APP_ID = app.config['FB_APP_ID']
FB_APP_NAME = app.config['FB_APP_NAME']
FB_APP_SECRET = app.config['FB_APP_SECRET']


@app.route('/')
def index():
    # If a user was set in the get_current_user function before the request,
    # the user is logged in.
    if g.user:
        # return render_template('index.html', app_id=FB_APP_ID,
        #                        app_name=FB_APP_NAME, user=g.user)
        return redirect(url_for('dashboard'))
    # Otherwise, a user is not logged in.
    return render_template('login.html', app_id=FB_APP_ID, name=FB_APP_NAME)


@app.route('/logout')
@login_required
def logout():
    """Log out the user from the application.
    Log out the user from the application by removing them from the
    session.  Note: this does not log the user out of Facebook - this is done
    by the JavaScript SDK.
    """
    session.pop('user', None)
    logout_user()
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard
    """
    graph = GraphAPI(g.user['access_token'])
    try:
        groups = graph.get_object(id='me/groups', fields='name,id,members,feed')
    except GraphAPIError as error:
        app.logger.error("Error: " + error.message)
        return redirect(url_for('logout'))
    # groups = graph.get_connections(id='me', connection_name='groups')
    app.logger.debug('groups: ' + str(groups))

    return render_template('dashboard.html', user=g.user, app_id=FB_APP_ID, name=FB_APP_NAME, groups=groups['data'])


@app.route('/dashboard/add_entry', methods=['GET', 'POST'])
@login_required
def add_entry():
    """Add entry
    """
    graph = GraphAPI(g.user['access_token'])
    if request.method == 'GET':
        try:
            groups = graph.get_object(id='me/groups', fields='name,id,members,feed')
        except GraphAPIError as error:
            app.logger.error("Error: " + error.message)
            return redirect(url_for('logout'))
        app.logger.debug('groups: ' + str(groups))

        return render_template('add_entry.html', user=g.user, app_id=FB_APP_ID, name=FB_APP_NAME, groups=groups['data'])
    else:
        groups = request.form.getlist('group_select')
        app.logger.debug("group_select: " + ','.join(groups))
        message = request.form.get('group_text', '')
        app.logger.debug("group_text: " + message)
        for group in groups:
            try:
                graph.put_object(group, "feed", message=message)
            except Exception as error:
                app.logger.error(error.message)

        return redirect(url_for('add_entry'))


@app.route('/about')
def about():
    return render_template('about.html', app_id=FB_APP_ID, name=FB_APP_NAME)


@app.before_request
def get_current_user():
    """Set g.user to the currently logged in user.
    Called before each request, get_current_user sets the global g.user
    variable to the currently logged in user.  A currently logged in user is
    determined by seeing if it exists in Flask's session dictionary.
    If it is the first time the user is logging into this application it will
    create the user and insert it into the database.  If the user is not logged
    in, None will be set to g.user.
    """

    # Set the user in the session dictionary as a global g.user and bail out
    # of this function early.
    if session.get('user'):
        app.logger.debug('session.get(\'user\') returns true')
        g.user = session.get('user')
        return

    # Attempt to get the short term access token for the current user.
    result = get_user_from_cookie(cookies=request.cookies, app_id=FB_APP_ID,
                                  app_secret=FB_APP_SECRET)

    # If there is no result, we assume the user is not logged in.
    if result:
        app.logger.debug('get_user_from_cookie returns true')
        # Check to see if this user is already in our database.
        user = User.query.filter(User.id == result['uid']).first()

        if not user:
            # Not an existing user so get info
            graph = GraphAPI(result['access_token'])
            profile = graph.get_object(id='me', fields='id,name,email,link')
            if 'link' not in profile:
                profile['link'] = ""

            if 'email' not in profile:
                profile['email'] = ""

            # Create the user and insert it into the database
            user = User(id=str(profile['id']), name=profile['name'],
                        email=profile['email'],
                        profile_url=profile['link'],
                        access_token=result['access_token'])
            db.session.add(user)
        elif user.access_token != result['access_token']:
            # If an existing user, update the access token
            user.access_token = result['access_token']

        # Add the user to the current session
        session['user'] = dict(name=user.name, profile_url=user.profile_url,
                               id=user.id, access_token=user.access_token)

        # Log in user using flask-login
        app.logger.debug('Logging in user: ' + user.name)
        login_user(user)

    # Commit changes to the database and set the user as a global g.user
    db.session.commit()
    g.user = session.get('user', None)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@login_manager.unauthorized_handler
def unauthorized():
    return render_template('login.html')
