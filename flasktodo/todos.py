
from flask import (
Blueprint, render_template, request, redirect, url_for, g, flash, session
)

from . import db

from werkzeug.security import check_password_hash, generate_password_hash

bp = Blueprint("todos", __name__)

@bp.route("/", methods=('GET', 'POST'))
def index():
    """View for home page which shows list of to-do items."""
    if request.method == 'POST':
        if "completed" in request.form:
            cur = db.get_db().cursor()
            cur.execute("SELECT * FROM todos WHERE completed = 'yes' AND author_id = %s ",
            (g.user['id'], )
            )
            dones = cur.fetchall()
            cur.close()
            return render_template("index.html", dones=dones)
        elif "uncompleted" in request.form:
            cur = db.get_db().cursor()
            cur.execute("SELECT * FROM todos WHERE completed = 'no' AND author_id = %s",
            (g.user['id'], )
            )
            undones = cur.fetchall()
            cur.close()
            return render_template("index.html", undones=undones)
        elif "delete" in request.form:
                id = request.form['delete']
                with db.get_db() as con:
                    with con.cursor() as cur:
                        cur.execute("DELETE FROM todos WHERE id = %s AND author_id = %s",
                        (id, g.user['id'], )
                        )
                cur = db.get_db().cursor()
                cur.execute('SELECT * FROM todos')
                todos = cur.fetchall()
                cur.close()
                return render_template("index.html", todos=todos)
        elif "finished" in request.form:
            id = request.form['finished']
            with db.get_db() as con:
                with con.cursor() as cur:
                    cur.execute("UPDATE todos SET completed=True WHERE id = %s AND author_id = %s",
                    (id,g.user['id'], )
                    )
                cur = db.get_db().cursor()
                cur.execute('SELECT * FROM todos')
                todos = cur.fetchall()
                cur.close()
                return render_template("index.html", todos=todos)
        elif "edit" in request.form:
            id = request.form['fix']
            description = request.form['edit']
            with db.get_db() as con:
                with con.cursor() as cur:
                    cur.execute(
                        'UPDATE todos SET description = %s WHERE id = %s AND author_id = %s',
                        (id, description, g.user['id'], )
                    )
            cur = db.get_db().cursor()
            cur.execute('SELECT * FROM todos WHERE author_id = %s',
            (g.user['id'], )
            )
            todos = cur.fetchall()
            cur.close()
            return render_template("index.html", todos=todos)
        todo = request.form['todo']
        with db.get_db() as con:
            with con.cursor() as cur:
                cur.execute("INSERT INTO todos(description, completed, created_at, author_id) VALUES(%s, %s, NOW(), %s)",
                (todo, False, g.user['id'])
                )
            if g.user['id'] is not None:
                cur = db.get_db().cursor()
                cur.execute('SELECT * FROM todos WHERE author_id = %s',
                (g.user['id'], )
                )
                todos = cur.fetchall()
                cur.close()
                return render_template("index.html", todos=todos)
    return render_template("index.html")

@bp.route("/register", methods=('GET','POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        cur = db.get_db().cursor()
        cur.execute("SELECT * FROM users WHERE username = %s",
        (username,)
        )
        check = cur.fetchone()
        cur.close()
        if not username:
            error = 'Username is required'
        elif not password:
            error = 'Password is required'
        elif check is not None:
            error = 'User {} is already registered.'.format(username)

        if error is None:
            with db.get_db() as con:
                with con.cursor() as cur:
                    cur.execute("INSERT INTO users(username, password) VALUES(%s, %s)",
                    (username, generate_password_hash(password))
                    )
                    return redirect(url_for('todos.login'))
        flash(error)

    return render_template('register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        error = None
        cur = db.get_db().cursor()
        cur.execute('SELECT * FROM users WHERE username = %s',
        (username,)
        )
        checkUser = cur.fetchone()
        cur.close()
        if checkUser is None:
            error = 'Log in information not valid'
        elif not check_password_hash(checkUser['password'], password):
            error = 'Incorrect password.'
        if error is None:
            session.clear()
            session['user_id'] = checkUser['id']
            return redirect(url_for('todos.index'))

        flash(error)
    return render_template('login.html')

@bp.route('/home', methods=('GET', 'POST'))
def private():
    return render_template('base.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        cur = db.get_db().cursor()
        cur.execute('SELECT * FROM users WHERE id = %s',
        (user_id,)
        )
        g.user = cur.fetchone()
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('todos.index'))
