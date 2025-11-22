import pytest
from app import create_app, db
from app.models import User, Post


@pytest.fixture
def test_app():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
    app.config["WTF_CSRF_ENABLED"] = False  # отключаем CSRF для тестов

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(test_app):
    return test_app.test_client()


def register(client, username, email, password="123456"):
    return client.post(
        "/auth/register",
        data={
            "username": username,
            "email": email,
            "password": password,
            "password2": password
        },
        follow_redirects=True
    )


def login(client, username, password="123456"):
    return client.post(
        "/auth/login",
        data={"username": username, "password": password},
        follow_redirects=True
    )


def test_register_new_user(client):
    r = register(client, "user1", "user1@example.com")

    assert r.status_code == 200
    assert b"Congratulations, you are now a registered user!" in r.data

    u = User.query.filter_by(username="user1").first()
    assert u is not None
    assert u.email == "user1@example.com"


def test_register_existing_email(client):
    register(client, "user1", "mail@example.com")
    r = register(client, "user2", "mail@example.com")

    assert b"Please use a different email address" in r.data


def test_login_and_session(client):
    register(client, "user2", "u2@example.com", "secret123")

    r = login(client, "user2", "secret123")

    assert r.status_code == 200
    assert b"Home" in r.data   # заголовок главной страницы


def test_create_post(client):
    register(client, "poster", "p@example.com")
    login(client, "poster")

    r = client.post(
        "/",
        data={"post": "Мой первый тестовый пост"},
        follow_redirects=True
    )

    assert r.status_code == 200
    assert b"Your post is now live!" in r.data

    p = Post.query.first()
    assert p is not None
    assert p.body == "Мой первый тестовый пост"


def test_edit_profile(client):
    register(client, "editor", "edit@example.com")
    login(client, "editor")

    r = client.post(
        "/edit_profile",
        data={
            "username": "editor_new",
            "about_me": "короткое описание"
        },
        follow_redirects=True
    )

    assert b"Your changes have been saved." in r.data

    u = User.query.filter_by(email="edit@example.com").first()
    assert u.username == "editor_new"
    assert u.about_me == "короткое описание"


def test_logout(client):
    register(client, "outuser", "out@example.com")
    login(client, "outuser")

    r = client.get("/auth/logout", follow_redirects=True)

    assert r.status_code == 200

    assert b"Sign In" in r.data
