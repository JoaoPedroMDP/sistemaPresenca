from datetime import datetime
import logging
from typing import Dict, List

from django.http import JsonResponse
from ninja import Router
from ninja.security import SessionAuth

from presenca.controllers.checkin_controller import CheckinController
from presenca.controllers.code_controller import CodeController
from presenca.controllers.ws_controller import WsController
from presenca.errors import UsedCodeError
from presenca.models import Code, Event, Member

checkin_router = Router()
lgr = logging.getLogger(__name__)


@checkin_router.get("/pending/{code_str}")
def get_pending_members(request, code_str: str):
    lgr.info(f"/checkin/pending/{code_str} - INICIO")
    lgr.info(f"Buscando membros que ainda não fizeram check-in. Código: '{code_str}'")
    try:
        code = Code.objects.get(code=code_str)
        CodeController.use_code(code)
        WsController.send_new_code_for_event(code.event)
    except UsedCodeError:
        lgr.info(f"Código '{code_str}' já foi usado. Retornando erro para o cliente.")
        return JsonResponse({
            "error_code": 400,
            "error": "Este código já foi usado. Escaneie o QR code novamente.",
        }, status=400)
    except Code.DoesNotExist:
        lgr.info(f"Código '{code_str}' não encontrado no banco. Retornando erro para o cliente.")
        return JsonResponse({
            "error_code": 404,
            "error": "Este código não existe! Escaneie o QR code novamente.",
        }, status=404)

    membs = [
        {"id": member.id, "name": member.name}
        for member in Member.didnt_checkin_today()
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
    member = Member.objects.get(id=m_id)
    code = Code.objects.get(code=code_str)

    if not member:
        return JsonResponse({"error_code": 404, "error": "Membro não encontrado no banco..."}, status=404)

    if not code:
        return JsonResponse({"error_code": 404, "error": "Código não encontrado no banco..."}, status=404)

    if not code.used:
        lgr.warning(
            f"Código {code_str} não foi marcado como usado, mas chegou na rota de checkin."
        )
        return JsonResponse({
            "error_code": 400,
            "error": "Problema com o código. Escaneie o QR code novamente.",
        }, status=400)

    if code.used_by and code.used_by != member:
        return JsonResponse({
            "error_code": 400,
            "error": "Este código já foi usado por outro membro. Escaneie o QR code novamente.",
        }, status=400)

    points = CheckinController.checkin_sabbath(member, code.used)
    code.assign_member(member)

    lgr.info(f"Membro '{member.name}' ganhou {points} pontos por ter feito checkin às {code.used}.")
    lgr.info(f"/checkin/{code_str}/{m_id} - FIM")
    return JsonResponse({"message": f"Presença marcada!", "points": points}, status=200)
