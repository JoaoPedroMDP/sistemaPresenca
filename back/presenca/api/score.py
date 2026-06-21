import logging

from ninja import Router
from ninja.security import SessionAuth

from presenca.controllers.score_controller import ScoreController
from presenca.models import Event, Member


score_router = Router()
lgr = logging.getLogger(__name__)

@score_router.get("/per-event", auth=SessionAuth())
def get_user_score_per_event(request):
    lgr.info(f"/score/per-event - INICIO")
    
    member = Member.objects.get(user=request.user)
    events = Event.objects.filter(checkin__member__id=member.id).distinct()
    return_data = {}
    for e in events:
        return_data[e.name] = ScoreController.get_user_score_for_event(member, e)

    lgr.info(f"Retornando pontuação de {member.name} nos eventos {[e.name for e in events]}.")
    lgr.info(f"/score/per-event - FIM")
    return return_data


@score_router.get("/event/{event_name}", auth=None)
def get_scoreboard_for_event(request, event_name: str):
    lgr.info(f"/score/event/{event_name} - INICIO")
    
    try:
        event = Event.objects.get(name=event_name)
    except Event.DoesNotExist:
        lgr.warning(f"Evento '{event_name}' não encontrado.")
        return {"success": False, "message": f"Evento '{event_name}' não encontrado."}

    scoreboard = ScoreController.get_scoreboard_for_event(event)
    lgr.info(f"Retornando placar para o evento '{event_name}'.")
    lgr.info(f"/score/event/{event_name} - FIM")
    return {"success": True, "data": scoreboard}
