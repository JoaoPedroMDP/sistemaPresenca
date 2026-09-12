from presenca.errors import (
    DeviceAlreadyActivatedError,
    DeviceNotActivatedError,
    DeviceRevokedError,
    ExpiredDeviceError,
)
from presenca.models import Device


class DeviceController:
    @staticmethod
    def activate(device: Device) -> Device:
        """
            Resgate do código pelo aparelho que leu o QR do admin.
            Uso único: o segundo resgate falha.
        """
        if device.revoked_at is not None:
            raise DeviceRevokedError("Device revoked")

        if not device.is_valid():
            raise ExpiredDeviceError("Device expired")

        if not device.activate():
            raise DeviceAlreadyActivatedError("Device already activated")

        return device

    @staticmethod
    def validate(device: Device) -> None:
        """
            Exigido em toda chamada do aparelho: o código é a credencial.
        """
        if device.revoked_at is not None:
            raise DeviceRevokedError("Device revoked")

        if device.activated_at is None:
            raise DeviceNotActivatedError("Device not activated")

        if not device.is_valid():
            raise ExpiredDeviceError("Device expired")
