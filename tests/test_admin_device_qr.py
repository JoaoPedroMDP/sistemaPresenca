from __future__ import annotations

from django.contrib.auth.models import User


def test_admin_change_page_shows_device_qr(client, device):
    """O QR de ativação é como o código chega ao aparelho: sem ninguém digitar."""
    User.objects.create_superuser("admin", "admin@example.com", "senha123")
    client.login(username="admin", password="senha123")

    response = client.get(f"/admin/presenca/device/{device.id}/change/")
    body = response.content.decode()

    assert response.status_code == 200
    assert "<svg" in body
    assert f"/checkin/device/{device.code}" in body


def test_admin_hides_qr_after_activation(client, active_device):
    User.objects.create_superuser("admin", "admin@example.com", "senha123")
    client.login(username="admin", password="senha123")

    response = client.get(f"/admin/presenca/device/{active_device.id}/change/")
    body = response.content.decode()

    assert f"/checkin/device/{active_device.code}" not in body
    assert "já resgatado" in body
