from datetime import date
import logging
from typing import Optional

from django.utils import timezone
from ninja import Router, Schema
from ninja.security import SessionAuth

from presenca.models import Member
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
    lgr.info(f"/member/me - INICIO")
    try:
        member = MemberRepository.get(user=request.user)
    except Member.DoesNotExist:
        lgr.error(f"Membro para usuário '{request.user.username}' não encontrado no banco.")

    if not member:
        lgr.info(f"Membro para usuário '{request.user.username}' não encontrado no banco.")
        return_data = {"error_code": 404, "error": "Membro não encontrado no banco..."}
    else:
        return_data = member

    lgr.info(f"/member/me - FIM")
    return return_data


@member_router.post("/photo", auth=SessionAuth(), response=MeResponse)
def set_photo(request):
    lgr.info(f"/member/photo - INICIO")
    member = MemberRepository.get(user=request.user)

    if not member:
        lgr.info(f"Membro para usuário '{request.user.username}' não encontrado no banco.")
        lgr.info(f"/member/photo - FIM")
        return {"error_code": 404, "error": "Membro não encontrado no banco..."}
    
    photo = request.FILES.get("photo")
    member.photo.delete(save=False)  # Exclui a foto antiga, se existir
    member.photo.save(member.slug() + "_profile_" + str(timezone.now()), photo)
    member.save()

    lgr.info(f"/member/photo - FIM")
    return member
