from datetime import datetime
import logging
from typing import Dict, List

from django.http import JsonResponse
from django.utils import timezone
from ninja import Router
from ninja.security import SessionAuth

from presenca.controllers.checkin_controller import CheckinController
from presenca.controllers.code_controller import CodeController
from presenca.errors import ExpiredCodeError
from presenca.models import Code, Event, Member

checkin_router = Router()
lgr = logging.getLogger(__name__)


@checkin_router.get("/pending/{code_str}")
def get_pending_members(request, code_str: str):
    lgr.info(f"/checkin/pending/{code_str} - INICIO")
    lgr.info(f"Buscando membros que ainda não fizeram check-in. Código: '{code_str}'")
    try:
        code = Code.objects.get(code=code_str)
        CodeController.validate_code(code)
    except ExpiredCodeError:
        lgr.info(f"Código '{code_str}' expirado. Retornando erro para o cliente.")
        return JsonResponse({
            "error_code": 400,
            "error": "Este código expirou. Escaneie o QR code novamente.",
        }, status=400)
    except Code.DoesNotExist:
        lgr.info(f"Código '{code_str}' não encontrado no banco. Retornando erro para o cliente.")
        return JsonResponse({
            "error_code": 404,
            "error": "Este código não existe! Escaneie o QR code novamente.",
        }, status=404)

    membs = [
        {"id": member.id, "name": member.name}
        for member in Member.didnt_checkin_today(code.event)
    ]

    lgr.info(f"{len(membs)} membros encontrados")
    lgr.info(f"/checkin/pending/{code_str} - FIM")
    return JsonResponse({"members": membs}, status=200)



@checkin_router.get(
    "/history", auth=SessionAuth(), response=Dict[str, List[datetime]]
)
def get_history(request):
    lgr.info(f"/checkin/history - INICIO")
    
    member = Member.objects.get(user=request.user)
    history = CheckinController.get_member_history(member)
    
    return_data = {}
    for e in history:
        return_data[e] = [c.date for c in history[e]]

    lgr.info(f"Histórico de check-ins do membro '{member.name}' retornado com {len(history)} registros.")
    lgr.info(f"/checkin/history - FIM")
    return JsonResponse(return_data, status=200)


@checkin_router.get(
    "/already/{event_name}", response=Dict[str, List[datetime]]
)
def get_checkins_today(request, event_name: str):
    lgr.info(f"/checkin/already/{event_name} - INICIO")
    
    event = Event.objects.get(name=event_name)
    checkins = CheckinController.get_checkins_today_for_event(event)
    members = [c.member for c in checkins]
    
    return_data = {
        "members": [m.to_checkin() for m in members],
    }

    return JsonResponse(return_data, status=200)


@checkin_router.post("/{code_str}/{m_id}")
def checkin(request, code_str: str, m_id: int):
    lgr.info(f"/checkin/{code_str}/{m_id} - INICIO")
    lgr.info(f"Check-in com código '{code_str}' e ID de membro '{m_id}'")
    try:
        member = Member.objects.get(id=m_id)
    except Member.DoesNotExist:
        return JsonResponse({"error_code": 404, "error": "Membro não encontrado no banco..."}, status=404)

    try:
        code = Code.objects.get(code=code_str)
    except Code.DoesNotExist:
        return JsonResponse({"error_code": 404, "error": "Código não encontrado no banco..."}, status=404)

    try:
        CodeController.validate_code(code)
    except ExpiredCodeError:
        return JsonResponse({
            "error_code": 400,
            "error": "Este código expirou. Escaneie o QR code novamente.",
        }, status=400)

    checkin_time = timezone.now()
    points = CheckinController.checkin(member, code.event, checkin_time)

    lgr.info(f"Membro '{member.name}' ganhou {points} pontos por ter feito checkin às {checkin_time}.")
    lgr.info(f"/checkin/{code_str}/{m_id} - FIM")
    return JsonResponse({"message": f"Presença marcada!", "points": points}, status=200)
