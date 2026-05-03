import logging

from ninja import Router
from ninja.security import SessionAuth

from presenca.controllers.score_controller import ScoreController
from presenca.models import Event
from presenca.repositories.member_repository import MemberRepository


score_router = Router()
lgr = logging.getLogger(__name__)

@score_router.get("/{event_name}", auth=SessionAuth())
def get_score(request, event_name: str):
    lgr.info(f"/score/{event_name} - INICIO")
    event = Event.objects.get(name=event_name)
    member = MemberRepository.get(user=request.user)

    score = ScoreController.get_score_for_event(member, event)
    lgr.info(f"Pontuação do membro '{member.name}' para o evento '{event.name}': {score} pontos.")
    lgr.info(f"/score/{event_name} - FIM")
    return {"score": score}
