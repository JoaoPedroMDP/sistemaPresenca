from datetime import datetime

from django.utils import timezone

from presenca.models import TimeScoreRules, Event
from presenca.repositories import Repository


class TimeScoreRulesRepository(Repository[TimeScoreRules]):
    model = TimeScoreRules

    @staticmethod
    def get_points_for_time_in_event(event: Event, checkin_time: datetime) -> float:
        tz_converted = checkin_time.astimezone(timezone.get_current_timezone())
        only_time = tz_converted.time()
        timescore = TimeScoreRules.objects.get(
            event=event,
            start_time__lte=only_time,
            end_time__gte=only_time
        )

        return timescore.points
