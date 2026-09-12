from __future__ import annotations

from datetime import timedelta

from django.utils import timezone
import pytest

from presenca.controllers.code_controller import CodeController
from presenca.controllers.device_controller import DeviceController
from presenca.errors import (
    DeviceAlreadyActivatedError,
    DeviceNotActivatedError,
    DeviceRevokedError,
    ExpiredDeviceError,
)
from presenca.models import Code, CheckIn, Device


def age_device(d: Device, days: int) -> None:
    Device.objects.filter(id=d.id).update(
        created_at=timezone.now() - timedelta(days=days)
    )
    d.refresh_from_db()


def test_device_is_valid_for_thirty_days(device):
    assert device.is_valid()

    age_device(device, Device.VALIDITY_DAYS - 1)
    assert device.is_valid()

    age_device(device, Device.VALIDITY_DAYS + 1)
    assert not device.is_valid()


def test_device_does_not_show_up_as_qr_code(event, device):
    # Tabelas separadas: o painel nem enxerga o código do aparelho
    current = CodeController.get_current_code(event)

    assert current.code != device.code
    assert Code.objects.filter(code=device.code).count() == 0


def test_activation_is_single_use(device):
    DeviceController.activate(device)

    with pytest.raises(DeviceAlreadyActivatedError):
        DeviceController.activate(device)


def test_revoked_device_is_invalid(active_device):
    active_device.revoked_at = timezone.now()
    active_device.save()

    with pytest.raises(DeviceRevokedError):
        DeviceController.validate(active_device)


def test_device_must_be_activated_before_use(device):
    with pytest.raises(DeviceNotActivatedError):
        DeviceController.validate(device)


def test_expired_device_is_rejected(active_device):
    age_device(active_device, Device.VALIDITY_DAYS + 1)

    with pytest.raises(ExpiredDeviceError):
        DeviceController.validate(active_device)


def test_qr_code_is_not_a_device_credential(client, code, member):
    response = client.get(f"/api/checkin/device/{code.code}/pending")

    assert response.status_code == 404


def test_activate_endpoint_returns_event(client, device):
    response = client.post(f"/api/checkin/device/{device.code}/activate")

    assert response.status_code == 200
    assert response.json()["event"] == device.event.name


def test_activate_endpoint_refuses_second_device(client, device):
    client.post(f"/api/checkin/device/{device.code}/activate")
    second = client.post(f"/api/checkin/device/{device.code}/activate")

    assert second.status_code == 409
    assert "outro aparelho" in second.json()["error"]


def test_activate_endpoint_with_qr_code_returns_404(client, code):
    response = client.post(f"/api/checkin/device/{code.code}/activate")

    assert response.status_code == 404


def test_device_pending_lists_members(client, active_device, member):
    response = client.get(f"/api/checkin/device/{active_device.code}/pending")

    assert response.status_code == 200
    assert response.json()["members"][0]["name"] == member.name


def test_device_pending_without_activation_returns_401(client, device, member):
    response = client.get(f"/api/checkin/device/{device.code}/pending")

    assert response.status_code == 401


def test_device_checkin_creates_checkin(client, active_device, member):
    response = client.post(f"/api/checkin/device/{active_device.code}/{member.id}")

    assert response.status_code == 200
    assert response.json()["points"] == 50.0
    assert CheckIn.objects.filter(member=member, event=active_device.event).count() == 1


def test_device_checkin_after_revoke_returns_401(client, active_device, member):
    active_device.revoked_at = timezone.now()
    active_device.save()

    response = client.post(f"/api/checkin/device/{active_device.code}/{member.id}")

    assert response.status_code == 401
    assert not CheckIn.objects.filter(member=member).exists()


def test_qr_checkin_route_still_works(client, code, member):
    response = client.post(f"/api/checkin/{code.code}/{member.id}")

    assert response.status_code == 200
