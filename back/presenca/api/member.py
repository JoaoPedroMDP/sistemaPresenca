from datetime import date
import logging
from typing import Optional

from ninja import Router, Schema
from ninja.security import SessionAuth

from presenca.repositories.member_repository import MemberRepository


member_router = Router()
lgr = logging.getLogger(__name__)

class MeUserResponse(Schema):
    id: int
    email: str

class MeResponse(Schema):
    id: int
    birthday: Optional[date]
    name: str
    user: MeUserResponse
    photo: str | None

@member_router.get("/me", auth=SessionAuth(), response=MeResponse)
def me(request):
    member = MemberRepository.get(user=request.user)

    if not member:
        return {"error_code": 404, "error": "Membro não encontrado no banco..."}

    return member
