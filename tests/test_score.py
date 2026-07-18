from __future__ import annotations

from datetime import datetime, time, timedelta

from django.utils import timezone

from presenca.controllers.score_controller import ScoreController
from presenca.models import CheckIn, Event, Member, TimeScoreRules


def _make_event_with_tiered_rules(db) -> Event:
    event = Event.objects.create(
        name="Culto Jovem",
        start=timezone.now() - timedelta(days=30),
        end=timezone.now() + timedelta(days=30),
    )
    TimeScoreRules.objects.create(
        event=event, start_time=time(0, 0), end_time=time(8, 59, 59), points=100
    )
    TimeScoreRules.objects.create(
        event=event, start_time=time(9, 0), end_time=time(23, 59, 59), points=70
    )
    return event


def _local_datetime(hour: int, minute: int = 0) -> datetime:
    today = timezone.localtime(timezone.now()).date()
    return timezone.make_aware(datetime.combine(today, time(hour, minute)))


def test_points_follow_time_rule_of_checkin(db):
    event = _make_event_with_tiered_rules(db)

    early = TimeScoreRules.get_points_for_time_in_event(event, _local_datetime(8, 30))
    late = TimeScoreRules.get_points_for_time_in_event(event, _local_datetime(10, 0))

    assert early == 100
    assert late == 70


def test_scoreboard_sums_and_orders_by_score(db):
    event = _make_event_with_tiered_rules(db)
    early_bird = Member.objects.create(name="Madrugadora")
    late_comer = Member.objects.create(name="Atrasado")

    CheckIn.objects.create(member=early_bird, event=event, date=_local_datetime(8, 0))
    CheckIn.objects.create(member=late_comer, event=event, date=_local_datetime(10, 0))

    scoreboard = ScoreController.get_scoreboard_for_event(event)

    assert scoreboard == [
        {"name": "Madrugadora", "score": 100},
        {"name": "Atrasado", "score": 70},
    ]


def test_event_without_rules_allows_checkin_with_zero_points(db):
    event = Event.objects.create(
        name="Evento Sem Placar",
        start=timezone.now() - timedelta(days=30),
        end=timezone.now() + timedelta(days=30),
    )
    member = Member.objects.create(name="Visitante")

    from presenca.controllers.checkin_controller import CheckinController

    points = CheckinController.checkin(member, event, timezone.now())

    assert points == 0.0
    assert CheckIn.objects.filter(member=member, event=event).count() == 1
    assert ScoreController.get_scoreboard_for_event(event) == [
        {"name": "Visitante", "score": 0.0}
    ]


def test_checkin_outside_all_rule_ranges_scores_zero(db):
    event = Event.objects.create(
        name="Evento Faixa Curta",
        start=timezone.now() - timedelta(days=30),
        end=timezone.now() + timedelta(days=30),
    )
    TimeScoreRules.objects.create(
        event=event, start_time=time(9, 0), end_time=time(10, 0), points=100
    )

    points = TimeScoreRules.get_points_for_time_in_event(event, _local_datetime(11, 0))

    assert points == 0.0


def test_didnt_checkin_today_excludes_member_with_checkin(db, event, member):
    other = Member.objects.create(name="Sem Presença")
    CheckIn.objects.create(member=member, event=event, date=timezone.now())

    pending = list(Member.didnt_checkin_today())

    assert pending == [other]
