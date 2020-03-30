from flask import Blueprint, render_template, request

from . import db


bp = Blueprint("todos", __name__)

@bp.route("/", methods=('GET', 'POST'))
def index():
    """View for home page which shows list of to-do items."""

    if request.method == 'POST':
        todo = request.form['todo']
        with db.get_db() as con:
            with con.cursor() as cur:
                cur.execute("INSERT INTO todos(description, completed, created_at) VALUES(%s, %s, NOW())",
                (todo, False)
                )
    cur = db.get_db().cursor()
    cur.execute('SELECT * FROM todos')
    todos = cur.fetchall()
    cur.close()

    return render_template("index.html", todos=todos)
