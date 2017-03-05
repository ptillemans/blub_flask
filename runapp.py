# all the imports
import time
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash

import arduino.protocol



app = Flask(__name__)
app.config.from_object(__name__)

g_arduino = None

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'runapp.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

def get_arduino():
    """Opens a connection to the arduino if there is none yet in the current
    application context"""
    global g_arduino
    if not g_arduino:
        print("Connecting to arduino")
        g_arduino = arduino.Arduino('/dev/ttyACM0', 9600)
        print("waiting to boot : 5s")
        time.sleep(5.0)
        print("setting time : 2s");
        g_arduino.set_time()
        time.sleep(2.0)
    return g_arduino

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')

@app.route("/")
def hello():
    arduino = get_arduino()
    status = arduino.get_status()
    return render_template('show_status.html', status=status)

@app.route("/manual_heat", methods=['POST'])
def manual_heat():
    arduino = get_arduino()
    status = arduino.activate_heating()
    return render_template('show_status.html', status=status)


get_arduino()

if __name__ == "__main__":
    print("initialize app")
    app.run(debug=True)
