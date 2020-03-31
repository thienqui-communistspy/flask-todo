from flask import Blueprint, render_template

from . import db


bp = Blueprint("todos", __name__)

@bp.route("/")
def index():
    """View for home page which shows list of to-do items."""

    cur = db.get_db().cursor()
    cur.execute('SELECT * FROM todos')
    todos = cur.fetchall()
    cur.close()

def crossoff():
    #need an if statement to begin with
    cur = db.get_db().cursor()
    cur.execute('')

    return render_template("index.html", todos=todos)
