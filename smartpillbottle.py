import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from contextlib import closing

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
        if request.form['emailInput'] != app.config['USERNAME']:
            error = 'Bad username or password.'
        elif request.form['passwordInput'] != app.config['PASSWORD']:
            error = 'Bad username or password.'
        else:
            session['logged_in'] = True
            flash('Login successful.')
            return redirect(url_for('show_users'))
    return render_template('login.html', error=error)


#
# Logout method
#
def logout():
    session.pop('logged_in', None)
    flash('Logout successful')
    return redirect(url_for('login'))


#
# Register
#
@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    return render_template('register.html', error=error)


if __name__ == '__main__':
    app.run()
