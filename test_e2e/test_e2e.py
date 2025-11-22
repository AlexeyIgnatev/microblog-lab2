import pytest

BASE_URL = "http://127.0.0.1:5000"


def test_full_flow(page):
    # ---------- Регистрация ----------
    page.goto(f"{BASE_URL}/auth/register")

    page.fill("input[name='username']", "e2euser")
    page.fill("input[name='email']", "e2euser@example.com")
    page.fill("input[name='password']", "secret123")
    page.fill("input[name='password2']", "secret123")

    page.click("input[type='submit']")

    assert "Congratulations, you are now a registered user!" in page.content()

    # ---------- Логин ----------
    page.goto(f"{BASE_URL}/auth/login")
    page.fill("input[name='username']", "e2euser")
    page.fill("input[name='password']", "secret123")
    page.click("input[type='submit']")

    assert "Home" in page.content()

    # ---------- Создание поста ----------
    page.fill("textarea[name='post']", "Это мой первый E2E пост!")
    page.click("input[type='submit']")

    assert "Your post is now live!" in page.content()

    # ---------- Редактирование профиля ----------
    page.goto(f"{BASE_URL}/edit_profile")

    page.fill("input[name='username']", "e2euser_new")
    page.fill("textarea[name='about_me']", "E2E тестирование работает!")
    page.click("input[type='submit']")

    assert "Your changes have been saved." in page.content()

    # ---------- Logout ----------
    page.goto(f"{BASE_URL}/auth/logout")

    assert "Sign In" in page.content()
