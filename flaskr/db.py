import psycopg2
from psycopg2.extras import DictCursor

import click
from flask import current_app, g

def get_db_conn():
    
    g.db = psycopg2.connect(
              host = 'localhost',
                database = 'flask_db',
                user = 'admin',
                password = 'admin',
                cursor_factory = DictCursor)

    cur = g.db.cursor()


    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    conn = get_db_conn()

    cur = conn.cursor()

    cur.execute('DROP TABLE IF EXISTS "user" cascade;'
                'DROP TABLE IF EXISTS post cascade;'

                'CREATE TABLE "user" ('
                'id SERIAL PRIMARY KEY,'
	            'username TEXT UNIQUE NOT NULL,'
	            'password TEXT NOT NULL'
                ');'

                'CREATE TABLE post('
	            'id SERIAL PRIMARY KEY ,'
	            'author_id INTEGER NOT NULL,'
	            'created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,'
	            'title TEXT NOT NULL,'
	            'body TEXT NOT NULL,'
                'FOREIGN KEY (author_id) REFERENCES "user" (id)'
                ');')

    conn.commit()
    cur.close()
    conn.close()
    

@click.command('init-db')
def init_db_command():
    #clear the existing data and create new tables
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

    

