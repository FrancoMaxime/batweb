from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

from werkzeug.exceptions import abort

from batweb.auth import login_required
from batweb.db import get_db

bp = Blueprint('terminal', __name__)


@bp.route('/terminal')
def index():
    db = get_db()
    terminals = db.execute('SELECT id, name, location, information, user_id FROM terminal ORDER BY name ASC').fetchall()

    return render_template('terminal/index.html', terminals=terminals)


def get_terminal(id, check_owner=True):
    """Get a terminal and its owner by id.
    Checks that the id exists and optionally that the current user is
    the owner.
    :param id: id of bat to get
    :param check_owner: require the current user to be the owner
    :return: the terminal with owner information
    :raise 404: if a terminal with the given id doesn't exist
    :raise 403: if the current user isn't the owner
    """
    terminal = (
        get_db()
        .execute("SELECT id, user_id, name, location, information FROM terminal WHERE id= ?", (id,),
                 )
        .fetchone()
    )

    if terminal is None:
        abort(404, "Terminal id {0} doesn't exist.".format(id))

    if check_owner and terminal["user_id"] != g.user["id"]:
        abort(403)

    return terminal


def set_terminal(name, location, information, mode, id=None):
    error = None

    if not name:
        error = 'You must enter a name.'
    elif not location:
        error = 'You must enter a location.'
    elif not information:
        error = 'You must give some information.'

    if error is not None:
        flash(error)
        if mode == "create":
            return render_template('terminal/create.html')
        elif mode == 'update':
            terminal = get_terminal(id)
            return render_template('terminal/update.html', terminal=terminal)
    elif mode == 'create':
        db = get_db()
        db.execute('INSERT INTO terminal (name, location, information, user_id) '
                   'VALUES (?,?,?,?)',
                   (name, location, information, g.user['id'])
                   )
        db.commit()
        return redirect(url_for('terminal.index'))
    elif mode == 'update':
        db = get_db()
        db.execute(
            "UPDATE terminal SET name = ?, location = ?, information = ? WHERE id = ?", (name, location, information, id)
        )
        db.commit()
        return redirect(url_for("terminal.index"))


@bp.route('/terminal/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        return set_terminal(request.form['name'], request.form['location'], request.form['information'], 'create')

    return render_template('terminal/create.html')


@bp.route("/terminal/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """Update a post if the current user is the author."""
    terminal = get_terminal(id)

    if request.method == "POST":
        return set_terminal(request.form['name'], request.form['location'], request.form['information'], 'update', id)

    return render_template("terminal/update.html", terminal=terminal)


@bp.route("/terminal/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    """Delete a detection.
    Ensures that the post exists and that the logged in user is the
    creator of the detection.
    """
    get_terminal(id)
    db = get_db()
    db.execute("DELETE FROM terminal WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("terminal.index"))