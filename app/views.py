from facebook import get_user_from_cookie, GraphAPI, GraphAPIError
from flask import g, render_template, redirect, request, session, url_for
from flask_login import login_user, logout_user, login_required

from app import app, db, login_manager, cache
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
    cache.delete_memoized(get_fb_groups, g.user['access_token'])
    session.pop('user', None)
    logout_user()
    app.logger.debug('User logout')
    return redirect(url_for('index'))


@cache.memoize(timeout=360)
def get_fb_groups(token):
    app.logger.debug('get_fb_groups')
    graph = GraphAPI(token)
    try:
        groups = graph.get_object(id='me/groups', fields='name,id,members,feed')
    except GraphAPIError as error:
        app.logger.error("GraphAPIError: " + error.message)
        return None
    except Exception as error:
        app.logger.error("Exception: " + error.message)
        return None
    app.logger.debug('groups: ' + str(groups))
    return groups['data']


@app.route('/dashboard')
@login_required
def dashboard():
    fb_groups = get_fb_groups(g.user['access_token'])
    if fb_groups is None:
        return redirect(url_for('logout'))
    return render_template('dashboard.html', user=g.user, app_id=FB_APP_ID, name=FB_APP_NAME, groups=fb_groups)


@app.route('/dashboard/add_entry', methods=['GET', 'POST'])
@login_required
def add_entry():
    if request.method == 'GET':
        fb_groups = get_fb_groups(g.user['access_token'])
        return render_template('add_entry.html', user=g.user, app_id=FB_APP_ID, name=FB_APP_NAME, groups=fb_groups)
    else:
        graph = GraphAPI(g.user['access_token'])
        groups = request.form.getlist('group_select')
        app.logger.debug("group_select: " + ','.join(groups))
        message = request.form.get('group_text', '')
        app.logger.debug("group_text: " + message)
        for group in groups:
            try:
                graph.put_object(group, "feed", message=message)
            except Exception as error:
                app.logger.error(error.message)
            else:
                cache.delete_memoized(get_fb_groups, g.user['access_token'])

        return redirect(url_for('add_entry'))


@app.route('/about')
def about():
    return render_template('about.html', app_id=FB_APP_ID, name=FB_APP_NAME)


@app.route('/privacy')
def privacy():
    return render_template('privacy.html', app_id=FB_APP_ID, name=FB_APP_NAME)


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
    if session.get('user', False):
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
    app.logger.debug('user_loader')
    return User.query.get(user_id)


@login_manager.unauthorized_handler
def unauthorized():
    app.logger.debug('unauthorized_handler')
    return render_template('login.html', app_id=FB_APP_ID, name=FB_APP_NAME)
