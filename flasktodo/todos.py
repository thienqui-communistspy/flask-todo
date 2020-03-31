from flask import Blueprint, render_template, request, redirect, url_for

from . import db


bp = Blueprint("todos", __name__)

@bp.route("/", methods=('GET', 'POST'))
def index():
    """View for home page which shows list of to-do items."""
    if request.method == 'POST':
        if "completed" in request.form:
            cur = db.get_db().cursor()
            cur.execute("SELECT * FROM todos WHERE completed = 'yes' ")
            dones = cur.fetchall()
            cur.close()
            return render_template("index.html", dones=dones)
        elif "uncompleted" in request.form:
            cur = db.get_db().cursor()
            cur.execute("SELECT * FROM todos WHERE completed = 'no' ")
            undones = cur.fetchall()
            cur.close()
            return render_template("index.html", undones=undones)
        elif "delete" in request.form:
                id = request.form['delete']
                with db.get_db() as con:
                    with con.cursor() as cur:
                        cur.execute("DELETE FROM todos WHERE id = %s",
                        (id,)
                        )
                cur = db.get_db().cursor()
                cur.execute('SELECT * FROM todos')
                todos = cur.fetchall()
                cur.close()
                return render_template("index.html", todos=todos)
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
