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

bp = Blueprint('detection', __name__)


@bp.route('/')
def index():
    db = get_db()
    detections = db.execute('SELECT d.id, detected, d.information, t.name as tname, location, b.name as bname, scientificname, description,'
                            't.user_id FROM detection d JOIN  terminal t ON d.terminal_id = t.id '
                            'JOIN bat b ON d.bat_id = b.id ORDER BY detected DESC').fetchall()

    return render_template('detection/index.html', detections=detections)


def get_detection(id, check_author=True):
    """Get a detection, its terminal and its creator by id.
    Checks that the id exists and optionally that the current user is
    the creator.
    :param id: id of detection to get
    :param check_author: require the current user to be the creator
    :return: the detection with creator information
    :raise 404: if a post with the given id doesn't exist
    :raise 403: if the current user isn't the creator
    """
    detection = (
        get_db()
        .execute("SELECT d.id, detected, d.information, t.name, location, b.name, scientificname, description, t.user_id "
                 "FROM detection d JOIN  terminal t ON d.terminal_id = t.id JOIN bat b ON d.bat_id = b.id "
                 "WHERE d.id= ?;", (id,),
                 )
        .fetchone()
    )

    if detection is None:
        abort(404, "Detection id {0} doesn't exist.".format(id))

    if check_author and detection["user_id"] != g.user["id"]:
        abort(403)
    return detection


def set_post(information, bat, terminal, mode, id=None):
    error = None
    db = get_db()
    b = db.execute("SELECT * FROM bat where id = ?", (bat,)).fetchone()
    t = db.execute("SELECT * FROM terminal where id = ?", (terminal,)).fetchone()
    if not bat or b is None:
        error = 'You must select a bat.'
    elif not terminal or t is None:
        error = 'You must select the terminal where the bat was detected.'
    elif not information:
        error = 'You must add some information about the detection.'

    if error is not None:
        flash(error)
        if mode == "create":
            return render_template('detection/create.html')
        elif mode == 'update':
            detection = get_detection(id)
            return render_template('detection/update.html', detection=detection)
    elif mode == 'create':
        db.execute('INSERT INTO detection (bat_id, terminal_id, information) '
                   'VALUES (?,?,?)',
                   (bat, terminal, information),
                   )
        db.commit()
        return redirect(url_for('detection.index'))
    elif mode == 'update':
        db.execute(
            "UPDATE detection SET information = ?, bat_id = ?, terminal_id = ? WHERE id = ?", (information, bat, terminal, id)
        )
        db.commit()
        return redirect(url_for("detection.index"))


@bp.route('/detection/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        return set_post(request.form['information'], request.form['bat'], request.form['terminal'], 'create')

    db = get_db()
    bats = db.execute('SELECT id, name, scientificname FROM bat')
    terminals = db.execute('SELECT id, name, location FROM terminal where user_id == (?)', (g.user['id'],),)

    return render_template('detection/create.html', bats=bats, terminals=terminals)


@bp.route("/detection/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """Update a post if the current user is the author."""
    detection = get_detection(id)

    if request.method == "POST":
        return set_post(request.form['information'], request.form['bat'], request.form['terminal'], 'update', id)

    db = get_db()
    bats = db.execute('SELECT id, name, scientificname FROM bat')
    terminals = db.execute('SELECT id, name, location FROM terminal where user_id == (?)', (g.user['id'],), )
    return render_template("detection/update.html", detection=detection, bats=bats, terminals=terminals)


@bp.route("/detection/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    """Delete a detection.
    Ensures that the post exists and that the logged in user is the
    creator of the detection.
    """
    get_detection(id)
    db = get_db()
    db.execute("DELETE FROM detection WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("detection.index"))