from __future__ import annotations

from datetime import timedelta

from django.utils import timezone
import pytest

from presenca.models import CheckIn, Event, Member


def test_member_with_checkin_today_is_not_pending(event, member):
    CheckIn.objects.create(member=member, event=event, date=timezone.now())

    assert member not in Member.didnt_checkin_today(event)


def test_member_with_checkin_yesterday_is_pending(event, member):
    CheckIn.objects.create(member=member, event=event, date=timezone.now() - timedelta(days=1))

    assert member in Member.didnt_checkin_today(event)


@pytest.mark.xfail(
    strict=True,
    reason="A1 do REVIEW.md: exclude() com relação multivalorada gera dois EXISTS independentes",
)
def test_checkin_yesterday_here_and_today_elsewhere_is_still_pending(event, member):
    """
        Membro veio ontem neste evento e hoje em outro evento. Nenhuma das
        duas presenças é "hoje neste evento", então ele deveria estar pendente.
    """
    other = Event.objects.create(name="Culto Jovem")
    CheckIn.objects.create(member=member, event=event, date=timezone.now() - timedelta(days=1))
    CheckIn.objects.create(member=member, event=other, date=timezone.now())

    assert member in Member.didnt_checkin_today(event)
