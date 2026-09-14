import logging
from typing import List

from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from ninja import Router, Schema

from presenca.controllers.checkin_controller import CheckinController
from presenca.models import CheckIn, Event, Member, Score, Scoreboard

dev_router = Router()
lgr = logging.getLogger(__name__)


class SimulateSchema(Schema):
    event: str
    member_ids: List[int]


def _forbidden_outside_debug():
    """
        O router só é montado com DEBUG ligado, mas cada rota confere de novo:
        uma montagem errada não pode virar uma rota de reset aberta.
    """
    if settings.DEBUG:
        return None

    return JsonResponse({
        "error_code": 404,
        "error": "Rota disponível apenas em desenvolvimento.",
    }, status=404)


def _event_or_error(event_name: str):
    try:
        return Event.objects.get(name=event_name), None
    except Event.DoesNotExist:
        return None, JsonResponse({
            "error_code": 404,
            "error": f"Evento '{event_name}' não encontrado.",
        }, status=404)


@dev_router.get("/events")
def get_events(request):
    if (error := _forbidden_outside_debug()):
        return error

    events = [e.name for e in Event.objects.all().order_by("name")]
    return JsonResponse({"events": events}, status=200)


@dev_router.get("/members/{event_name}")
def get_members(request, event_name: str):
    if (error := _forbidden_outside_debug()):
        return error

    event, error = _event_or_error(event_name)
    if error or not event:
        return error

    pending_ids = set(
        Member.didnt_checkin_today(event).values_list("id", flat=True)
    )
    members = [
        {
            **member.to_checkin(),
            "id": member.id,
            "checked_in_today": member.id not in pending_ids,
        }
        for member in Member.objects.all().order_by("name")
    ]

    return JsonResponse({"event": event.name, "members": members}, status=200)


@dev_router.post("/checkin")
def simulate_checkin(request, payload: SimulateSchema):
    if (error := _forbidden_outside_debug()):
        return error

    event, error = _event_or_error(payload.event)
    if error or not event:
        return error

    today = timezone.localtime(timezone.now()).date()
    results = []
    for member_id in payload.member_ids:
        try:
            member = Member.objects.get(id=member_id)
        except Member.DoesNotExist:
            results.append({
                "id": member_id,
                "name": None,
                "points": None,
                "already": False,
                "error": "Membro não encontrado.",
            })
            continue

        # Lido antes do checkin: depois dele sempre existiria um registro e não
        # daria mais para dizer se o painel foi realmente notificado
        already = CheckIn.objects.filter(
            member=member, event=event, date__date=today
        ).exists()

        points = CheckinController.checkin(member, event, timezone.now())
        results.append({
            "id": member.id,
            "name": member.name,
            "points": points,
            "already": already,
        })

    lgr.info(f"[dev] {len(results)} checkins simulados no evento '{event.name}'.")
    return JsonResponse({"results": results}, status=200)


@dev_router.post("/reset")
def reset(request):
    if (error := _forbidden_outside_debug()):
        return error

    deleted = {
        "checkins": CheckIn.objects.all().delete()[0],
        "scores": Score.objects.all().delete()[0],
        "scoreboards": Scoreboard.objects.all().delete()[0],
    }

    lgr.warning(f"[dev] Reset executado: {deleted}")
    return JsonResponse({"deleted": deleted}, status=200)
