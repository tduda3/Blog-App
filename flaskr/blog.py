from flask import (
        Blueprint, flash, g, redirect, render_template, request, url_for
)

from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db_conn

bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute(
            'SELECT p.id, title, body, created, author_id, username'
            ' FROM post p JOIN "user" u ON p.author_id = u.id'
            ' ORDER BY created DESC'
        )

    posts = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('blog/index.html', posts=posts)

@bp.route('/create', methods=('GET','POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            conn = get_db_conn()
            cur = conn.cursor()
            cur.execute(
                    'INSERT INTO post (title, body, author_id)'
                    ' VALUES (%s, %s, %s)',
                    (title, body, g.user['id'])
            )

            conn.commit()
            cur.close()
            conn.close()
            return redirect(url_for('blog.index'))
    return render_template('blog/create.html')

def get_post(id, check_author=True):
    
    conn = get_db_conn()
    cur = conn.cursor()

    cur.execute(
            'SELECT p.id, title, body, created, author_id, username'
            ' FROM post p JOIN "user" u ON p.author_id = u.id'
            ' WHERE p.id = %s',
            (id,)
    )

    post = cur.fetchone()
    cur.close()
    conn.close()
        

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)

        else:
            conn = get_db_conn()
            cur = conn.cursor()
            
            cur.execute(
                'UPDATE post SET title = %s, body = %s'
                ' WHERE id = %s',
                (title, body, id)
            )
            conn.commit()
            cur.close()
            conn.close()
            return redirect(url_for('blog.index'))
    return render_template('blog/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)

    conn = get_db_conn()
    cur = conn.cursor()
    
    cur.execute('DELETE FROM post WHERE id = %s', (id,))
    conn.commit()

    cur.close()
    conn.close()
    return redirect(url_for('blog.index'))


