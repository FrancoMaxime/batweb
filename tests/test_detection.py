import pytest

from batweb.db import get_db


def test_index(client, auth):
    response = client.get("/")
    assert b"Log In" in response.data
    assert b"Register" in response.data

    auth.login()
    response = client.get("/")
    assert b"Log Out" in response.data
    assert b"terminal 1" in response.data
    assert b"bat 1" in response.data
    assert b"information LAC" in response.data
    assert b'href="/detection/1/update"' in response.data
    assert b"terminal 2" in response.data
    assert b"bat 2" in response.data
    assert b"information FORET" in response.data
    assert b'href="/detection/2/update"' in response.data


@pytest.mark.parametrize("path", ("/detection/create", "/detection/1/update", "/detection/1/delete"))
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers["Location"] == "http://localhost/auth/login"


def test_author_required(app, client, auth):
    # change the post author to another user
    with app.app_context():
        db = get_db()
        db.execute("UPDATE terminal SET user_id = 2 WHERE id = 1")
        db.commit()

    auth.login()

    # current user can't modify other user's post
    assert client.post("/detection/1/update").status_code == 403
    assert client.post("/detection/1/delete").status_code == 403
    # current user doesn't see edit link
    assert b'href="/detection/1/update"' not in client.get("/").data


@pytest.mark.parametrize("path", ("/detection/3/update", "/detection/3/delete"))
def test_exists_required(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 404


def test_create(client, auth, app):
    auth.login()
    assert client.get("/detection/create").status_code == 200
    client.post("/detection/create", data={"bat": "1", "terminal": "1", "information": "information"})

    with app.app_context():
        db = get_db()
        count = db.execute("SELECT COUNT(id) FROM detection").fetchone()[0]
        assert count == 3

        detection = db.execute("SELECT * FROM detection WHERE id = 3").fetchone()
        assert detection["bat_id"] == 1
        assert detection["terminal_id"] == 1
        assert detection["information"] == "information"


def test_update(client, auth, app):
    auth.login()
    assert client.get("/detection/1/update").status_code == 200
    client.post("/detection/1/update", data={"bat": "2", "terminal": "2", "information": "information updated"})

    with app.app_context():
        db = get_db()
        detection = db.execute("SELECT * FROM detection WHERE id = 1").fetchone()
        print(detection.keys())
        assert detection["bat_id"] == 2
        assert detection["terminal_id"] == 2
        assert detection["information"] == "information updated"


@pytest.mark.parametrize(
    ("bat", "terminal", "information", "message"),
    (
        ("", "1", "information", b"You must select a bat."),
        ("1", "", "information", b"You must select the terminal where the bat was detected."),
        ("1", "1", "", b"You must add some information about the detection."),
        ("15", "1", "information", b"You must select a bat."),
        ("1", "15", "information", b"You must select the terminal where the bat was detected."),
    ),
)
def test_create_update_validate(client, auth, bat, terminal, information, message):
    auth.login()
    response = client.post("/detection/create", data={"bat": bat, "terminal": terminal, "information": information})
    assert message in response.data
    response = client.post("/detection/1/update", data={"bat": bat, "terminal": terminal, "information": information})
    assert message in response.data


def test_delete(client, auth, app):
    auth.login()
    response = client.post("/detection/1/delete")
    assert response.headers["Location"] == "http://localhost/"

    with app.app_context():
        db = get_db()
        detection = db.execute("SELECT * FROM detection WHERE id = 1").fetchone()
        assert detection is None
