from __future__ import annotations

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings


def test_member_me_returns_current_member(authenticated_client, member, user):
    response = authenticated_client.get("/api/member/me")

    assert response.status_code == 200
    assert response.json() == {
        "id": member.id,
        "birthday": "2000-01-02",
        "name": member.name,
        "user": {
            "id": user.id,
            "email": user.email,
        },
        "photo": None,
    }


def test_member_me_returns_404_when_user_has_no_member(authenticated_client, db):
    other_user = User.objects.create_user(
        username="sem-membro",
        email="sem-membro@example.com",
        password="senha123",
    )
    authenticated_client.force_login(other_user)

    response = authenticated_client.get("/api/member/me")

    assert response.status_code == 404
    assert response.json() == {
        "error_code": 404,
        "error": "Membro não encontrado no banco...",
    }


@override_settings(
    STORAGES={
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
            "OPTIONS": {
                "location": "/tmp/sistema-presenca-tests-media",
                "base_url": "/media/",
            },
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
)
def test_member_photo_upload_updates_member_photo(authenticated_client, member):
    upload = SimpleUploadedFile(
        name="profile.png",
        content=b"fake image bytes",
        content_type="image/png",
    )

    response = authenticated_client.post(
        "/api/member/photo",
        data={"photo": upload},
    )

    assert response.status_code == 200

    member.refresh_from_db()
    assert member.photo.name.startswith("images/members/")
    assert response.json()["photo"] is not None

def test_member_photo_without_file_returns_400(authenticated_client, member):
    response = authenticated_client.post("/api/member/photo", data={})

    assert response.status_code == 400
    member.refresh_from_db()
    assert not member.photo


def test_member_photo_rejects_non_image(authenticated_client, member):
    upload = SimpleUploadedFile(
        name="notes.txt", content=b"texto", content_type="text/plain"
    )

    response = authenticated_client.post("/api/member/photo", data={"photo": upload})

    assert response.status_code == 400
    assert "imagem" in response.json()["error"]


def test_member_photo_rejects_files_over_limit(authenticated_client, member):
    from presenca.api.member import PHOTO_MAX_BYTES

    upload = SimpleUploadedFile(
        name="huge.png", content=b"0" * (PHOTO_MAX_BYTES + 1), content_type="image/png"
    )

    response = authenticated_client.post("/api/member/photo", data={"photo": upload})

    assert response.status_code == 400
    assert "5 MB" in response.json()["error"]


def test_member_photo_without_member_returns_404(authenticated_client, db):
    upload = SimpleUploadedFile(name="p.png", content=b"x", content_type="image/png")

    response = authenticated_client.post("/api/member/photo", data={"photo": upload})

    assert response.status_code == 404
