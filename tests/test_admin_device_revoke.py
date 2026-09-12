from __future__ import annotations

from django.contrib.auth.models import User
import pytest

from presenca.models import Device


@pytest.fixture
def admin_client(client, db):
    User.objects.create_superuser("admin", "admin@example.com", "senha123")
    client.login(username="admin", password="senha123")
    return client


def test_revoke_action_sets_revoked_at(admin_client, active_device):
    response = admin_client.post(
        "/admin/presenca/device/",
        {"action": "revoke", "_selected_action": [active_device.pk]},
        follow=True,
    )

    active_device.refresh_from_db()
    assert response.status_code == 200
    assert active_device.revoked_at is not None
    assert "1 dispositivo(s) revogado(s)." in response.content.decode()


def test_revoke_action_keeps_first_revocation_date(admin_client, active_device):
    admin_client.post(
        "/admin/presenca/device/",
        {"action": "revoke", "_selected_action": [active_device.pk]},
    )
    active_device.refresh_from_db()
    first = active_device.revoked_at

    response = admin_client.post(
        "/admin/presenca/device/",
        {"action": "revoke", "_selected_action": [active_device.pk]},
        follow=True,
    )

    active_device.refresh_from_db()
    assert active_device.revoked_at == first
    assert "0 dispositivo(s) revogado(s)." in response.content.decode()


def test_revoked_device_is_refused_by_api(admin_client, client, active_device, member):
    admin_client.post(
        "/admin/presenca/device/",
        {"action": "revoke", "_selected_action": [active_device.pk]},
    )

    response = client.get(f"/api/checkin/device/{active_device.code}/pending")

    assert response.status_code == 401
    assert Device.objects.get(pk=active_device.pk).revoked_at is not None
