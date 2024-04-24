import functools

from flask import (
        Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db_conn

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET','POST'))
def register():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_conn()
        cur = conn.cursor()
        error = None

        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."

        if error is None:
            try:
                cur.execute(
                        'INSERT INTO "user" (username,password) VALUES (%s, %s)',
                        (username, generate_password_hash(password)),
                )
                conn.commit()
                cur.close()
                conn.close()
            except conn.IntegrityError:
                error = f"User {username} is already registered."

            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')

@bp.route("/login", methods=('GET', 'POST'))
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        conn = get_db_conn()
        cur = conn.cursor()
        error = None

        cur.execute(
                'SELECT * FROM "user" WHERE username = %s', (username,)
                    )

        user = cur.fetchone()
        cur.close()
        conn.close()

        if user is None:
            error = 'Inccorect username.'
        elif not check_password_hash(user[2], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user[0]
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute('SELECT * FROM "user" WHERE id = %s', (user_id,))

        g.user = cur.fetchone()
        cur.close()
        conn.close()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)
    return wrapped_view
