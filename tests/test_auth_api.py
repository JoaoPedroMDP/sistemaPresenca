from __future__ import annotations


def test_login_with_valid_credentials_returns_200(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": "joao", "password": "senha123"},
        content_type="application/json",
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Login bem-sucedido."}


def test_login_with_wrong_password_returns_401(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": "joao", "password": "errada"},
        content_type="application/json",
    )

    assert response.status_code == 401
    assert response.json()["error"] == "Credenciais inválidas."


def test_login_with_empty_fields_returns_400(client, db):
    response = client.post(
        "/api/auth/login",
        data={"username": "", "password": ""},
        content_type="application/json",
    )

    assert response.status_code == 400
