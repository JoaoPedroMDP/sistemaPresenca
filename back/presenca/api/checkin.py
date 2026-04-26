from datetime import datetime
import logging
from typing import List, Optional

from ninja import Router, Schema
from ninja.security import SessionAuth

from presenca.controllers.checkin_controller import CheckinController
from presenca.controllers.code_controller import CodeController
from presenca.controllers.ws_controller import WsController
from presenca.errors import UsedCodeError
from presenca.models import Code
from presenca.repositories.code_repository import CodeRepository
from presenca.repositories.member_repository import MemberRepository

checkin_router = Router()
lgr = logging.getLogger(__name__)


@checkin_router.get("/pending/{code_str}")
def get_pending_members(request, code_str: str):
    try:
        code = CodeRepository.get(code=code_str)
        CodeController.use_code(code)
        WsController.send_new_code_for_event(code.event)
    except UsedCodeError:
        return {
            "error_code": 400,
            "error": "Este código já foi usado. Escaneie o QR code novamente.",
        }
    except Code.DoesNotExist:
        return {
            "error_code": 404,
            "error": "Este código não existe! Escaneie o QR code novamente.",
        }

    membs = [
        {"id": member.id, "name": member.name}
        for member in MemberRepository.didnt_checkin_today()
    ]

    return {"members": membs}


@checkin_router.post("/{code_str}/{m_id}")
def checkin(request, code_str: str, m_id: int):
    lgr.info(f"Check-in with code: {code_str} and member ID: {m_id}")
    member = MemberRepository.get(id=m_id)
    code = CodeRepository.get(code=code_str)

    if not member:
        return {"error_code": 404, "error": "Membro não encontrado no banco..."}

    if not code:
        return {"error_code": 404, "error": "Código não encontrado no banco..."}

    if not code.used:
        lgr.warning(f"Código {code_str} não foi marcado como usado, mas chegou na rota de checkin.")
        return {
            "error_code": 400,
            "error": "Problema com o código. Escaneie o QR code novamente.",
        }

    if code.used_by and code.used_by != member:
        return {
            "error_code": 400,
            "error": "Este código já foi usado por outro membro. Escaneie o QR code novamente.",
        }

    points = CheckinController.checkin_sabbath(member, code.used)
    CodeRepository.assign_member(code, member)

    return {"message": f"Presença marcada!", "points": points}


class HistoryCheckinResponse(Schema):
    date: Optional[datetime]

@checkin_router.get("/history", auth=SessionAuth(), response=List[HistoryCheckinResponse])
def get_history(request):
    member = MemberRepository.get(user=request.user)
    history = CheckinController.get_member_history(member)

    return history