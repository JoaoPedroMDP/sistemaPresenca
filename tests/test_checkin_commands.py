from __future__ import annotations

from datetime import timedelta

from django.core.management import call_command
from django.utils import timezone
import pytest

from presenca.models import CheckIn, Event, Member


@pytest.fixture
def checkin(event, member) -> CheckIn:
    return CheckIn.objects.create(
        member=member, event=event, date=timezone.now() - timedelta(hours=1)
    )


def test_export_writes_one_row_per_checkin(tmp_path, monkeypatch, checkin):
    monkeypatch.chdir(tmp_path)

    call_command("export_checkins")

    rows = (tmp_path / "checkins.csv").read_text().splitlines()
    assert rows == [f"{checkin.event.name},{checkin.member.name},{checkin.date.isoformat()}"]


def test_import_creates_event_member_and_checkin(tmp_path, db):
    when = timezone.now().replace(microsecond=0)
    csv_file = tmp_path / "in.csv"
    csv_file.write_text(f"Culto Jovem,Maria Souza,{when.isoformat()}\n")

    call_command("import_checkins", str(csv_file))

    event = Event.objects.get(name="Culto Jovem")
    member = Member.objects.get(name="Maria Souza")
    assert member.user is not None
    assert CheckIn.objects.filter(event=event, member=member, date=when).count() == 1


def test_import_is_idempotent(tmp_path, db):
    when = timezone.now().replace(microsecond=0)
    csv_file = tmp_path / "in.csv"
    csv_file.write_text(f"Culto Jovem,Maria Souza,{when.isoformat()}\n")

    call_command("import_checkins", str(csv_file))
    call_command("import_checkins", str(csv_file))

    assert CheckIn.objects.count() == 1
    assert Member.objects.filter(name="Maria Souza").count() == 1


def test_export_then_import_round_trips(tmp_path, monkeypatch, checkin):
    monkeypatch.chdir(tmp_path)
    call_command("export_checkins")
    CheckIn.objects.all().delete()

    call_command("import_checkins", str(tmp_path / "checkins.csv"))

    restored = CheckIn.objects.get()
    assert restored.member == checkin.member
    assert restored.event == checkin.event
    assert restored.date == checkin.date
