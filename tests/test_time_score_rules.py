from __future__ import annotations

from datetime import time

from django.core.exceptions import ValidationError
import pytest

from presenca.models import Event, TimeScoreRules


@pytest.fixture
def culto(db) -> Event:
    return Event.objects.create(name="Culto")


def test_rule_with_end_before_start_is_invalid(culto):
    rule = TimeScoreRules(event=culto, start_time=time(10, 0), end_time=time(9, 0), points=10)

    with pytest.raises(ValidationError) as exc:
        rule.full_clean()

    assert "end_time" in exc.value.message_dict


def test_overlapping_rule_in_same_event_is_invalid(culto):
    TimeScoreRules.objects.create(event=culto, start_time=time(8, 0), end_time=time(9, 0), points=100)
    rule = TimeScoreRules(event=culto, start_time=time(8, 30), end_time=time(9, 30), points=70)

    with pytest.raises(ValidationError) as exc:
        rule.full_clean()

    assert "sobrepõe" in str(exc.value)


def test_adjacent_rules_do_not_overlap(culto):
    TimeScoreRules.objects.create(event=culto, start_time=time(8, 0), end_time=time(9, 0), points=100)
    rule = TimeScoreRules(event=culto, start_time=time(9, 0, 1), end_time=time(10, 0), points=70)

    rule.full_clean()  # não lança


def test_same_range_in_other_event_is_allowed(culto):
    other = Event.objects.create(name="Outro")
    TimeScoreRules.objects.create(event=other, start_time=time(8, 0), end_time=time(9, 0), points=100)
    rule = TimeScoreRules(event=culto, start_time=time(8, 0), end_time=time(9, 0), points=100)

    rule.full_clean()


def test_editing_a_rule_does_not_overlap_with_itself(culto):
    rule = TimeScoreRules.objects.create(event=culto, start_time=time(8, 0), end_time=time(9, 0), points=100)
    rule.points = 90

    rule.full_clean()
