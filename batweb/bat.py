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

bp = Blueprint('bat', __name__)


@bp.route('/bat')
def index():
    db = get_db()
    bats = db.execute('SELECT id, name, scientificname, description, user_id FROM bat ORDER BY name ASC ').fetchall()

    return render_template('bat/index.html', bats=bats)


def get_bat(id, check_author=True):
    """Get a bat and its creator by id.
    Checks that the id exists and optionally that the current user is
    the creator.
    :param id: id of bat to get
    :param check_author: require the current user to be the creator
    :return: the detection with creator information
    :raise 404: if a bat with the given id doesn't exist
    :raise 403: if the current user isn't the creator
    """
    bat = (
        get_db()
        .execute("SELECT id, user_id, name, scientificname, description FROM bat WHERE id= ?", (id,),
                 )
        .fetchone()
    )

    if bat is None:
        abort(404, "Bat id {0} doesn't exist.".format(id))

    if check_author and bat["user_id"] != g.user["id"]:
        abort(403)

    return bat


def set_bat(name, scientificname, description, mode, id=None):
    error = None

    if not name:
        error = 'You must enter a name.'
    elif not scientificname:
        error = 'You must enter a scientific name.'
    elif not description:
        error = 'You must enter a description.'

    if error is not None:
        flash(error)
        if mode == "create":
            return render_template('bat/create.html')
        elif mode == 'update':
            bat = get_bat(id)
            return render_template('bat/update.html', bat=bat)
    elif mode == 'create':
        db = get_db()
        db.execute('INSERT INTO bat (name, scientificname, description, user_id) '
                   'VALUES (?,?,?,?)',
                   (name, scientificname, description, g.user['id'])
                   )
        db.commit()
        return redirect(url_for('bat.index'))
    elif mode == 'update':
        db = get_db()
        db.execute(
            "UPDATE bat SET name = ?, scientificname = ?, description = ? WHERE id = ?",
            (name, scientificname, description, id)
        )
        db.commit()
        return redirect(url_for("bat.index"))


@bp.route('/bat/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        return set_bat(request.form['name'], request.form['scientificname'], request.form['description'], 'create')

    return render_template('bat/create.html')


@bp.route("/bat/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """Update a post if the current user is the author."""
    bat = get_bat(id)
    if request.method == "POST":
        return set_bat(request.form['name'], request.form['scientificname'], request.form['description'], 'update', id)

    return render_template("bat/update.html", bat=bat)


@bp.route("/bat/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    """Delete a detection.
    Ensures that the post exists and that the logged in user is the
    creator of the detection.
    """
    get_bat(id)
    db = get_db()
    db.execute("DELETE FROM bat WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("bat.index"))
