import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, jsonify
from contextlib import closing
import queries
# ######################################################################################################################
# Flask configuration and setup
# ######################################################################################################################

# Database configuration
DATABASE = 'database.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

# Create the application
app = Flask(__name__)
app.config.from_object(__name__)


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


# Database initialization function, can call from outside to make the database
def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


# Set up database scaffolding for requests
@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


# ######################################################################################################################
# Application routes
# ######################################################################################################################

#
# Default route
#
@app.route('/')
def checkLogin():
    if session.get('logged_in'):
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))


#
# Show users
#
@app.route('/show_users')
def show_users():
    cur = g.db.execute('SELECT type, name FROM accounts')
    entries = [dict(type=row[0], name=row[1]) for row in cur.fetchall()]
    return render_template('show_users.html', entries=entries)


#
# Add users
#
@app.route('/add_user', methods=['POST'])
def add_user():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('INSERT INTO accounts (type, name, email, password) VALUES (?, ?, ?, ?)',
                 [request.form['userType'], request.form['userName'], request.form['userEmail'],
                  request.form['userPassword']])
    g.db.commit()
    flash('User added.')
    return redirect(url_for('show_users'))


#
# Login
#
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['emailInput']
        password = request.form['passwordInput']

        if email == '':
            error = 'Please enter an account name.'
        if password == '':
            error = 'Please enter a password.'


        cur = g.db.execute(queries.SELECT_ACCOUNT_BY_EMAIL, (email,))
        entries = [dict(passwd=row[3]) for row in cur.fetchall()]

        good = False
        if len (entries) > 0:
            if password == entries[0].get('passwd'):
                good = True

        if not good:
            error = 'Bad account name or password.'
        else:
            session['logged_in'] = True
            session['email'] = email
            flash('Login successful.')
            return redirect(url_for('dashboard'))
    return render_template('login.html', error=error)


#
# Logout method
#
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('logged_in', None)
    session.pop('email', None)
    flash('Logout successful')
    return redirect(url_for('login'))


#
# Register
#
@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        name = request.form['nameInput']
        email = request.form['emailInput']
        password = request.form['passwordInput']
        type = request.form['typeRadios']

        if type == '':
            error = 'Please select an account type.'
        if password == '':
            error = 'Please enter a password.'
        if email == '':
            error = 'Please enter an account name.'
        if name == '':
            error = 'Please enter a full name.'

        # Check if this user already exists...
        cur = g.db.execute(queries.SELECT_ACCOUNT_BY_EMAIL, (email,))
        entries = [dict(email=row[2]) for row in cur.fetchall()]
        if len(entries) > 0:
            error = 'Account name already exists.'

        if error is not None:
            return render_template('register.html', error=error)

        g.db.execute(queries.INSERT_ACCOUNT, (name, email, password, type))
        g.db.commit()

        flash("Account successfully registered.")
        return redirect(url_for('login'))
    return render_template('register.html', error=error)


#
# Dashboard
#
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    error = None

    if not session.get('logged_in'):
        error = 'You must be logged in to use this page.'
        return render_template('login.html', error=error)

    cur = g.db.execute(queries.SELECT_ACCOUNT_BY_EMAIL, (session.get('email'),));
    entries = [dict(type=row[4]) for row in cur.fetchall()]

    if entries[0].get('type') == 'caregiver':
        return render_template('dashboard_caregiver.html', error=error)
    elif entries[0].get('type') == 'patient':
        return render_template('dashboard_patient.html', error=error)
    else:
        error = 'Invalid user type: ' + entries[0].type # XXX: XSS
        return render_template('login.html', error=error)


#
# API Methods
#

#
# List medicine that needs to be taken today (actually, within 24 hours of the timestamp)
#
@app.route('/data/schedule/<username>/<timestamp>', methods=['GET'])
def schedule(username, timestamp):
    print('Getting schedule for ' + username + ' on ' + str(timestamp))
    return jsonify({'success': True})
#
# When the user takes or untakes pills, let us know.
#
@app.route('/data/take', methods=['POST'])
def take():
    content = request.json

    if not content:
        return jsonify({'success': False, 'error': 'Make sure request content-type is application/json...'})

    if not 'username' in content:
        return jsonify({'success': False, 'error': 'Please provide a username.'})

    if not 'items' in content:
        return jsonify({'success': False, 'error': 'Please provide an items (name, timestamp) list.'})

    username = content['username']
    items = content['items']

    if not isinstance(items, list):
        return jsonify({'success': False, 'error': 'Items must be a list of (name, timestamp) tuples.'})

    # TODO: Okay, the sanity checking ends here. Make sure you're providing 'name', 'timestamp', 'taken' fields
    print('User ' + username + ' just told us:')
    for i in items:
        print('\tDose of ' + i.get('name') + ' at ' + str(i.get('timestamp')) + ' - taken: ' + str(i.get('taken')))

    # TODO: Check for closest instance of this pill that needs to be taken...

    return jsonify({    'success': True, 'error': 'So far so good, hello ' + username})

if __name__ == '__main__':
    app.run()