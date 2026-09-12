import logging

from django.http import JsonResponse
from django.utils import timezone
from ninja import Router

from presenca.controllers.checkin_controller import CheckinController
from presenca.controllers.device_controller import DeviceController
from presenca.errors import (
    DeviceAlreadyActivatedError,
    DeviceNotActivatedError,
    DeviceRevokedError,
    ExpiredDeviceError,
)
from presenca.models import Device, Member

device_router = Router()
lgr = logging.getLogger(__name__)


def _device_or_error(code_str: str):
    try:
        return Device.objects.get(code=code_str), None
    except Device.DoesNotExist:
        lgr.info(f"Dispositivo com código '{code_str}' não encontrado.")
        return None, JsonResponse({
            "error_code": 404,
            "error": "Este código não existe. Peça um novo QR Code.",
        }, status=404)


def _validated_device_or_error(code_str: str):
    """
        O código do aparelho é a credencial: sem ele válido e já ativado, a
        rota não responde nada útil.
    """
    device, error = _device_or_error(code_str)
    if error or not device:
        return None, error

    try:
        DeviceController.validate(device)
    except DeviceNotActivatedError:
        return None, JsonResponse({
            "error_code": 401,
            "error": "Este dispositivo ainda não foi ativado.",
        }, status=401)
    except DeviceRevokedError:
        return None, JsonResponse({
            "error_code": 401,
            "error": "O acesso deste dispositivo foi revogado.",
        }, status=401)
    except ExpiredDeviceError:
        return None, JsonResponse({
            "error_code": 401,
            "error": "O acesso deste dispositivo expirou. Peça um novo QR Code.",
        }, status=401)

    return device, None


@device_router.post("/{code_str}/activate")
def activate_device(request, code_str: str):
    """
        Resgate do código pelo aparelho que leu o QR mostrado no admin.
        Uso único: só o primeiro aparelho é liberado.
    """
    lgr.debug(f"/checkin/device/{code_str}/activate - INICIO")

    device, error = _device_or_error(code_str)
    if error:
        return error

    try:
        DeviceController.activate(device)
    except DeviceAlreadyActivatedError:
        lgr.info(f"Código '{code_str}' já havia sido resgatado.")
        return JsonResponse({
            "error_code": 409,
            "error": "Este código já foi usado em outro aparelho.",
        }, status=409)
    except DeviceRevokedError:
        return JsonResponse({
            "error_code": 403,
            "error": "O acesso deste dispositivo foi revogado.",
        }, status=403)
    except ExpiredDeviceError:
        return JsonResponse({
            "error_code": 400,
            "error": "Este código expirou. Peça um novo QR Code.",
        }, status=400)

    lgr.info(f"Dispositivo '{device}' ativado para o evento '{device.event.name}'.")
    lgr.debug(f"/checkin/device/{code_str}/activate - FIM")
    return JsonResponse({
        "event": device.event.name,
        "label": device.label,
        "expiresAt": device.expires_at().isoformat(),
    }, status=200)


@device_router.get("/{code_str}/pending")
def get_pending_members(request, code_str: str):
    lgr.debug(f"/checkin/device/{code_str}/pending - INICIO")

    device, error = _validated_device_or_error(code_str)
    if error:
        return error

    membs = [
        m.to_checkin() | {"id": m.id}
        for m in Member.didnt_checkin_today(device.event)
    ]

    lgr.info(f"{len(membs)} membros pendentes no evento '{device.event.name}'")
    lgr.debug(f"/checkin/device/{code_str}/pending - FIM")
    return JsonResponse({"event": device.event.name, "members": membs}, status=200)


@device_router.post("/{code_str}/{m_id}")
def device_checkin(request, code_str: str, m_id: int):
    """
        Check-in feito no aparelho liberado. Sem QR rotativo: a proteção é a
        posse do código do dispositivo.
    """
    lgr.debug(f"/checkin/device/{code_str}/{m_id} - INICIO")

    device, error = _validated_device_or_error(code_str)
    if error:
        return error

    try:
        member = Member.objects.get(id=m_id)
    except Member.DoesNotExist:
        return JsonResponse({"error_code": 404, "error": "Membro não encontrado no banco..."}, status=404)

    checkin_time = timezone.now()
    points = CheckinController.checkin(member, device.event, checkin_time)

    lgr.info(f"Membro '{member.name}' ganhou {points} pontos pelo dispositivo '{device}'.")
    lgr.debug(f"/checkin/device/{code_str}/{m_id} - FIM")
    return JsonResponse({"message": "Presença marcada!", "points": points}, status=200)
