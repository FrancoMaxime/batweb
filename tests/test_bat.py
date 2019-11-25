import pytest

from batweb.db import get_db


def test_index(client, auth):
    response = client.get("/")
    assert b"Log In" in response.data
    assert b"Register" in response.data

    auth.login()
    response = client.get("/bat")
    assert b"Log Out" in response.data
    assert b"bat 1" in response.data
    assert b"name 1" in response.data
    assert b"description 1" in response.data
    assert b'href="/bat/1/update"' in response.data
    assert b"bat 2" in response.data
    assert b"name 2" in response.data
    assert b"description 2" in response.data
    assert b'href="/bat/2/update"' in response.data


@pytest.mark.parametrize("path", ("/bat/create", "/bat/1/update", "/bat/1/delete"))
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers["Location"] == "http://localhost/auth/login"


def test_author_required(app, client, auth):
    # change the post author to another user
    with app.app_context():
        db = get_db()
        db.execute("UPDATE bat SET user_id = 2 WHERE id = 1")
        db.commit()

    auth.login()

    # current user can't modify other user's post
    assert client.post("/bat/1/update").status_code == 403
    assert client.post("/bat/1/delete").status_code == 403
    # current user doesn't see edit link
    assert b'href="bat/1/update"' not in client.get("/bat").data


@pytest.mark.parametrize("path", ("/bat/3/update", "/bat/3/delete"))
def test_exists_required(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 404


def test_create(client, auth, app):
    auth.login()
    assert client.get("/bat/create").status_code == 200
    client.post("/bat/create", data={"name": "created", "scientificname": "scientific", "description": "description"})

    with app.app_context():
        db = get_db()
        count = db.execute("SELECT COUNT(id) FROM bat").fetchone()[0]
        test = 3

        assert count == test
        bat = db.execute("SELECT * FROM bat WHERE id = 3").fetchone()
        assert bat["name"] == "created"
        assert bat["scientificname"] == "scientific"
        assert bat["description"] == "description"


def test_update(client, auth, app):
    auth.login()
    assert client.get("/bat/1/update").status_code == 200
    client.post("/bat/1/update", data={"name": "updated", "scientificname": "scientific name", "description": "information updated"})

    with app.app_context():
        db = get_db()
        bat = db.execute("SELECT * FROM bat WHERE id = 1").fetchone()
        assert bat["name"] == "updated"
        assert bat["scientificname"] == "scientific name"
        assert bat["description"] == "information updated"


@pytest.mark.parametrize(
    ("name", "scientificname", "description", "message"),
    (
        ("", "test", "description", b"You must enter a name."),
        ("test", "", "description", b"You must enter a scientific name."),
        ("test", "a", "", b"You must enter a description.")
    ),
)
def test_create_update_validate(client, auth, name, scientificname, description, message):
    auth.login()
    response = client.post("/bat/create", data={"name": name, "scientificname": scientificname, "description": description})
    assert message in response.data
    response = client.post("/bat/1/update", data={"name": name, "scientificname": scientificname, "description": description})
    assert message in response.data


def test_delete(client, auth, app):
    auth.login()
    response = client.post("bat/1/delete")
    assert response.headers["Location"] == "http://localhost/bat"

    with app.app_context():
        db = get_db()
        bat = db.execute("SELECT * FROM bat WHERE id = 1").fetchone()
        assert bat is None
