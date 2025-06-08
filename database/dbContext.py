import pkgutil

from flask import Flask, g
import sqlite3

app = Flask(__name__)
DATABASE = 'articleDatabase.db'

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_app(app):
    app.teardown_appcontext(close_db)
    create_db_if_missing()


def create_db_if_missing():
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()

    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name=?
    """, ("InsertLog",))

    table_exists = cursor.fetchone()

    if not table_exists:
        sql_script = pkgutil.get_data('database', 'dbCreateScript.sql').decode('utf-8')
        cursor.executescript(sql_script)
        db.commit()
