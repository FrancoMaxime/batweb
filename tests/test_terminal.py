import pytest

from batweb.db import get_db


def test_index(client, auth):
    response = client.get("/")
    assert b"Log In" in response.data
    assert b"Register" in response.data

    auth.login()
    response = client.get("/terminal")
    assert b"Log Out" in response.data
    assert b"terminal 1" in response.data
    assert b"Louvain La Neuve FORET" in response.data
    assert b"information 1" in response.data
    assert b'href="/terminal/1/update"' in response.data
    assert b"terminal 2" in response.data
    assert b"Louvain La Neuve LAC" in response.data
    assert b"information 2" in response.data
    assert b'href="/terminal/2/update"' in response.data


@pytest.mark.parametrize("path", ("/terminal/create", "/terminal/1/update", "/terminal/1/delete"))
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
    assert client.post("/terminal/1/update").status_code == 403
    assert client.post("/terminal/1/delete").status_code == 403
    # current user doesn't see edit link
    assert b'href="terminal/1/update"' not in client.get("/terminal").data


@pytest.mark.parametrize("path", ("/terminal/3/update", "/terminal/3/delete"))
def test_exists_required(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 404


def test_create(client, auth, app):
    auth.login()
    assert client.get("/terminal/create").status_code == 200
    client.post("/terminal/create", data={"name": "created", "location": "location", "information": "information"})

    with app.app_context():
        db = get_db()
        count = db.execute("SELECT COUNT(id) FROM terminal").fetchone()[0]
        assert count == 3

        terminal = db.execute("SELECT * FROM terminal WHERE id = 3").fetchone()
        assert terminal["name"] == "created"
        assert terminal["location"] == "location"
        assert terminal["information"] == "information"


def test_update(client, auth, app):
    auth.login()
    assert client.get("/terminal/1/update").status_code == 200
    client.post("/terminal/1/update", data={"name": "updated", "location": "location updated", "information": "information updated"})

    with app.app_context():
        db = get_db()
        terminal = db.execute("SELECT * FROM terminal WHERE id = 1").fetchone()
        assert terminal["name"] == "updated"
        assert terminal["location"] == "location updated"
        assert terminal["information"] == "information updated"


@pytest.mark.parametrize(
    ("name", "location", "information", "message"),
    (
        ("", "test", "information", b"You must enter a name."),
        ("test", "", "information", b"You must enter a location."),
        ("test", "a", "", b"You must give some information.")
    ),
)
def test_create_update_validate(client, auth, name, location, information, message):
    auth.login()
    response = client.post("/terminal/create", data={"name": name, "location": location, "information": information})
    assert message in response.data
    response = client.post("/terminal/1/update", data={"name": name, "location": location, "information": information})
    assert message in response.data


def test_delete(client, auth, app):
    auth.login()
    response = client.post("/terminal/1/delete")
    assert response.headers["Location"] == "http://localhost/terminal"

    with app.app_context():
        db = get_db()
        terminal = db.execute("SELECT * FROM terminal WHERE id = 1").fetchone()
        assert terminal is None
