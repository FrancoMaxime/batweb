import pytest
from flask import g
from flask import session

from batweb.db import get_db


def test_register(client, app):
    # test that viewing the page renders without template errors
    assert client.get("/auth/register").status_code == 200

    # test that successful registration redirects to the login page
    response = client.post("/auth/register", data={"mail": "a", 'firstname': 'b', 'lastname':'c', "password1": "Password1", "password2": "Password1"})
    assert "http://localhost/auth/login" == response.headers["Location"]

    # test that the user was inserted into the database
    with app.app_context():
        assert (
            get_db().execute("select * from user where mail = 'a'").fetchone()
            is not None
        )


@pytest.mark.parametrize(
    ("mail", "firstname", "lastname", "password1", "password2", "message"),
    (
        ("", "", "", "", "", b"Mail is required."),
        ("a", "", "", "", "", b"Firstname is required."),
        ("a", "b", "", "", "", b"Lastname is required."),
        ("a", "b", "c", "", "", b"Password is required."),
        ("a", "b", "c", "Password1", "Password2", b"Passwords must be the same."),
        ("test", "b", "c", "Password1", "Password1", b"Mail test is already registered."),
    ),
)
def test_register_validate_input(client, mail, firstname, lastname, password1, password2, message):
    response = client.post(
        "/auth/register", data={"mail": mail, 'firstname': firstname, 'lastname': lastname, "password1": password1, "password2": password2}
    )
    assert message in response.data


def test_login(client, auth):
    # test that viewing the page renders without template errors
    assert client.get("/auth/login").status_code == 200

    # test that successful login redirects to the index page
    response = auth.login()
    assert response.headers["Location"] == "http://localhost/"

    # login request set the user_id in the session
    # check that the user is loaded from the session
    with client:
        client.get("/")
        assert session["user_id"] == 1
        assert g.user["mail"] == "test"


@pytest.mark.parametrize(
    ("mail", "password", "message"),
    (("a", "test", b"Incorrect mail."), ("test", "a", b"Incorrect password.")),
)
def test_login_validate_input(auth, mail, password, message):
    response = auth.login(mail, password)
    assert message in response.data


def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert "user_id" not in session
