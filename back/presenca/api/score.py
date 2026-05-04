import logging

from ninja import Router
from ninja.security import SessionAuth

from presenca.controllers.score_controller import ScoreController
from presenca.models import Event
from presenca.repositories.member_repository import MemberRepository


score_router = Router()
lgr = logging.getLogger(__name__)

@score_router.get("/per-event", auth=SessionAuth())
def get_score_per_event(request):
    lgr.info(f"/score/per-event - INICIO")
    
    member = MemberRepository.get(user=request.user)
    events = Event.objects.filter(checkin__member__id=member.id).distinct()
    return_data = {}
    for e in events:
        return_data[e.name] = ScoreController.get_score_for_event(member, e)

    lgr.info(f"Retornando pontuação de {member.name} nos eventos {[e.name for e in events]}.")
    lgr.info(f"/score/per-event - FIM")
    return return_data
