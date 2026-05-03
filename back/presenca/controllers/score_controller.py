

from presenca.controllers.checkin_controller import CheckinController
from presenca.controllers.scoreboard_controller import ScoreboardController
from presenca.models import Event, Member
from presenca.repositories.timescorerules_repository import TimeScoreRulesRepository


class ScoreController:
    @staticmethod
    def get_score_for_event(member: Member, event: Event) -> float:
        checkins = CheckinController.get_checkins_for_event_member(event, member)
        total_points = 0
        for c in checkins:
            total_points += TimeScoreRulesRepository.get_points_for_time_in_event(event=event, checkin_time=c.date)

        return total_points