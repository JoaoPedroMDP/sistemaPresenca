from datetime import time

from presenca.models import TimeScoreRules, Event
from presenca.repositories import Repository


class TimeScoreRulesRepository(Repository[TimeScoreRules]):
    model = TimeScoreRules

    @staticmethod
    def get_points_for_time_in_event(event_name: str, checkin_time: time) -> float:
        event = Event.objects.get(name=event_name)
        timescore = TimeScoreRules.objects.get(
            event=event,
            start_time__lte=checkin_time,
            end_time__gte=checkin_time
        )

        return timescore.points
