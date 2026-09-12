from datetime import date
import logging
from typing import Optional

from django.http import JsonResponse
from django.utils import timezone
from ninja import Router, Schema
from ninja.security import SessionAuth

from presenca.models import Member


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
    lgr.debug(f"/member/me - INICIO")
    try:
        member = Member.objects.get(user=request.user)
    except Member.DoesNotExist:
        lgr.error(f"Membro para usuário '{request.user.username}' não encontrado no banco.")
        return JsonResponse({"error_code": 404, "error": "Membro não encontrado no banco..."}, status=404)

    lgr.debug(f"/member/me - FIM")
    return member


# Limite do upload de foto de perfil. O front já recorta para 400x400 JPEG,
# então qualquer coisa perto disso é um cliente fora do fluxo normal.
PHOTO_MAX_BYTES = 5 * 1024 * 1024


@member_router.post("/photo", auth=SessionAuth(), response=MeResponse)
def set_photo(request):
    lgr.debug(f"/member/photo - INICIO")
    try:
        member = Member.objects.get(user=request.user)
    except Member.DoesNotExist:
        lgr.warning(f"Usuário '{request.user.username}' não tem membro associado.")
        return JsonResponse({"error_code": 404, "error": "Membro não encontrado no banco..."}, status=404)

    photo = request.FILES.get("photo")
    if photo is None:
        return JsonResponse({"error_code": 400, "error": "Envie o arquivo no campo 'photo'."}, status=400)

    if not (photo.content_type or "").startswith("image/"):
        return JsonResponse({"error_code": 400, "error": "O arquivo precisa ser uma imagem."}, status=400)

    if photo.size > PHOTO_MAX_BYTES:
        return JsonResponse({"error_code": 400, "error": "Imagem acima de 5 MB."}, status=400)

    member.photo.delete(save=False)  # Exclui a foto antiga, se existir
    member.photo.save(member.slug() + "_profile_" + str(timezone.now()), photo)
    member.save()

    lgr.debug(f"/member/photo - FIM")
    return member
