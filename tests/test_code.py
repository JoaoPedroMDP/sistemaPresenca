from __future__ import annotations

from datetime import timedelta

from django.utils import timezone
import pytest

from presenca.code_timer import CodeTimerRegistry
from presenca.controllers.code_controller import CodeController
from presenca.errors import ExpiredCodeError
from presenca.models import Code


def test_fresh_code_is_valid(code):
    assert code.is_valid()


def test_expires_at_is_validity_window_after_creation(code):
    assert code.expires_at() == code.created_at + timedelta(seconds=Code.validity_seconds())


def test_rotates_at_is_rotation_window_after_creation(code):
    assert code.rotates_at() == code.created_at + timedelta(seconds=Code.rotation_seconds())


def test_validity_is_rotation_plus_grace(db):
    assert Code.validity_seconds() == Code.rotation_seconds() + Code.VALIDITY_GRACE_SECONDS


def test_old_code_is_not_valid(expired_code):
    assert not expired_code.is_valid()


def test_validate_code_raises_for_expired(expired_code):
    with pytest.raises(ExpiredCodeError):
        CodeController.validate_code(expired_code)


def test_get_current_code_reuses_fresh_code(event, code):
    assert CodeController.get_current_code(event) == code


def test_get_current_code_replaces_code_older_than_rotation(event, code):
    # Ainda válido para check-in, mas velho demais para ser exibido no painel
    Code.objects.filter(id=code.id).update(
        created_at=timezone.now() - timedelta(seconds=Code.rotation_seconds() + 1)
    )

    current = CodeController.get_current_code(event)

    assert current != code
    assert current.is_valid()


def test_rotate_code_always_creates_new(event, code):
    rotated = CodeController.rotate_code(event)

    assert rotated != code
    assert Code.objects.filter(event=event).count() == 2


def test_code_timer_stops_only_after_last_listener_leaves(event):
    group_name = event.as_websocket_group_name()

    CodeTimerRegistry.add_listener(event)
    CodeTimerRegistry.add_listener(event)
    timer = CodeTimerRegistry._timers[group_name]
    assert timer.thread.is_alive()

    CodeTimerRegistry.remove_listener(group_name)
    assert group_name in CodeTimerRegistry._timers

    CodeTimerRegistry.remove_listener(group_name)
    assert group_name not in CodeTimerRegistry._timers
    timer.thread.join(timeout=2)
    assert not timer.thread.is_alive()
