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
        entries = [dict(name=row[1], passwd=row[3], type=row[4]) for row in cur.fetchall()]

        good = False
        if len (entries) > 0:
            if password == entries[0].get('passwd'):
                good = True

        if not good:
            error = 'Bad account name or password.'
        else:
            # Load session values from the database entry corresponding to this account.
            session['logged_in'] = True
            session['email'] = email
            session['name'] = entries[0].get('name') # Full name
            session['type'] = entries[0].get('type') # Patient or caregiver?
            flash('Login successful. Hello ' + session['name'] + '!')
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

    if session['type'] == 'caregiver':
        cur = g.db.execute(queries.SELECT_PATIENTS_BY_CAREGIVER_EMAIL, (session['email'],))
        return render_template('dashboard_caregiver.html', error=error, patients=cur.fetchall())
    elif session['type'] == 'patient':
        cur = g.db.execute(queries.SELECT_PRESCRIPTIONS_BY_PATIENT_EMAIL, (session['email'],))
        prescriptions = cur.fetchall()
        print(prescriptions)
        return render_template('dashboard_patient.html', error=error, prescriptions=prescriptions)
    else:
        error = 'Invalid user type: ' + session['type'] # XXX: XSS
        return render_template('login.html', error=error)


#
# API Endpoints
#

#
# List medicine that needs to be taken today (actually, within 24 hours of the timestamp)
#
@app.route('/data/schedule/<username>/<timestamp>', methods=['GET'])
def schedule(username, timestamp):
    timestamp = int(timestamp)

    # Determine upper and lower bound for day containing the given timestamp...
    lowerBound = timestamp - (timestamp % (60 * 60 * 24))
    upperBound = (timestamp + 60 * 60 * 24) - (timestamp % (60 * 60 * 24))
    print('Getting schedule for ' + username + ' between ' + str(lowerBound) + ', ' + str(upperBound))

    cur = g.db.execute(queries.SELECT_DOSES_BY_TIME_BETWEEN, (username, lowerBound, upperBound))
    entries = [dict(prescriptionName=row[2], time=row[3], taken=row[5]) for row in cur.fetchall()]

    return jsonify({'success': True, 'items': entries})
#
# When the user takes or untakes pills, let us know. The timestamp sent will identify which dose the app is referencing,
# and the actualTime field will say when this dose was actually taken.
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
        return jsonify({'success': False, 'error': 'Items must be a list of (name, timestamp, actualTime) tuples.'})

    # TODO: Okay, the sanity checking ends here. Make sure you're providing 'name', 'timestamp', 'taken' fields
    print('User ' + username + ' just told us:')
    for i in items:
        print('\tDose of ' + i.get('name') + ' at ' + str(i.get('doseTime')) + ' - taken: ' + str(i.get('taken')) + ' actual time: ' + str(i.get('actualTime')))

        # Two cases - ether the dose time is known and we're retroactively setting one, or we have to estmate based
        # on the actualTime (i.e. doseTime is 0.)

        if (i.get('doseTime') != 0):
            print('\t\tDose time known, updating the actualTime and taken.')
            g.db.execute(queries.UPDATE_ACTUAL_TIME_AND_TAKEN_BY_DOSE_TIME, (i.get('actualTime'), i.get('taken'), i.get('doseTime')))
            g.db.commit()
            continue

        print('\t\tUnknown dose time, finding closest dose to time ' + str(i.get('actualTime')))
        timestamp = i.get('actualTime')
        lowerBound = timestamp - (timestamp % (60 * 60 * 24))
        upperBound = (timestamp + 60 * 60 * 24) - (timestamp % (60 * 60 * 24))
        print('Will be between ' + str(lowerBound) + ' and ' + str(upperBound))

        cur = g.db.execute(queries.SELECT_DOSES_BY_TIME_BETWEEN, (username, lowerBound, upperBound))
        entries = [dict(prescriptionName=row[2], time=row[3], taken=row[5]) for row in cur.fetchall()]
        print('\t\tFound ' + str(len(entries)) + ' candidates...')

        bestDistance = 86400
        bestEntry = None

        for e in entries:
            delta = abs(e.get('time') - timestamp)
            print('\t\t\tFound an entry ' + str(delta) + ' away')
            if (delta < bestDistance):
                print('\t\t\t... it was better.')
                bestDistance = delta
                bestEntry = e

        if bestEntry is None:
            print("\t\tNO DOSE FOUND!")
            continue
        print(bestEntry)
        print('\t\tUpdating dose at ' + str(bestEntry.get('time')) + ', setting taken = ' + str(i.get('taken')))
        g.db.execute(queries.UPDATE_ACTUAL_TIME_AND_TAKEN_BY_DOSE_TIME, (i.get('actualTime'), i.get('taken'), bestEntry.get('time')));
        g.db.commit()
    return jsonify({'success': True, 'error': 'Ok.'})

if __name__ == '__main__':
    app.run()