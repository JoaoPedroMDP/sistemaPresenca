import logging
from uuid import uuid4

from ninja import Router

from ponto.controllers.checkin_controller import CheckinController
from ponto.controllers.code_controller import CodeController
from ponto.errors import UsedCodeError
from ponto.models import Code
from ponto.repositories.checkin_repository import CheckinRepository
from ponto.repositories.code_repository import CodeRepository
from ponto.repositories.member_repository import MemberRepository

router = Router()
lgr = logging.getLogger(__name__)

@router.post("/checkin/{code_str}/{m_id}")
def checkin(request, code_str: str, m_id: int):
    lgr.info(f"Check-in with code: {code_str} and member ID: {m_id}")
    member = MemberRepository.get_by_id(m_id)
    code = CodeRepository.get_by_code(code_str)

    if not member:
        return {
            "error_code": 404,
            "error": "Membro não encontrado no banco..."}
    
    if not code:
        return {
            "error_code": 404,
            "error": "Código não encontrado no banco..."}
    
    if code.used_by and code.used_by != member:
        return {
            "error_code": 400,
            "error": "Este código já foi usado por outro membro. Escaneie o QR code novamente."}

    points = CheckinController.checkin_sabbath(member)
    CodeRepository.assign_member(code, member)

    return {
        "message": f"Presença marcada!",
        "points": points
    }

@router.get("/members/pending/{code}")
def get_members(request, code: str):
    try:
        CodeController.use_code(code)
    except UsedCodeError as e:
        return {
            "error_code": 400,
            "error": "Este código já foi usado. Escaneie o QR code novamente."}
    except Code.DoesNotExist:
        return {
            "error_code": 404,
            "error": "Este código não existe! Escaneie o QR code novamente."}

    membs = [
        {"id": member.id, "name": member.name} 
        for member in MemberRepository.didnt_checkin_today()
    ]


    return {"members": membs}
