from presenca.controllers.checkin_controller import CheckinController
from presenca.models import Event, Member
from presenca.repositories.timescorerules_repository import TimeScoreRulesRepository


class ScoreController:
    @staticmethod
    def get_user_score_for_event(member: Member, event: Event) -> float:
        checkins = CheckinController.get_member_checkins_for_event(event, member)
        total_points = 0
        for c in checkins:
            total_points += TimeScoreRulesRepository.get_points_for_time_in_event(event=event, checkin_time=c.date)

        return total_points
    
    @staticmethod
    def get_scoreboard_for_event(event: Event) -> list[dict]:
        checkins = CheckinController.get_checkins_for_event(event)
        member_scores = {}
        for c in checkins:
            if c.member.id not in member_scores:
                member_scores[c.member.id] = {
                    "name": c.member.name,
                    "score": 0
                }
            member_scores[c.member.id]["score"] += TimeScoreRulesRepository.get_points_for_time_in_event(event=event, checkin_time=c.date)

        # Ordenar por pontuação
        sorted_scores = sorted(member_scores.values(), key=lambda x: x["score"], reverse=True)
        return sorted_scores
