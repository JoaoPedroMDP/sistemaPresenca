from __future__ import annotations

from datetime import date, timedelta

import pytest

from django.contrib.auth.models import User
from django.utils import timezone

from presenca.constants import DAY_END, DAY_START
from presenca.models import Code, Event, Member, TimeScoreRules


@pytest.fixture(autouse=True)
def _test_hosts(settings):
    settings.ALLOWED_HOSTS = ["testserver"]


@pytest.fixture
def user(db) -> User:
    return User.objects.create_user(
        username="joao",
        email="joao@example.com",
        password="senha123",
    )


@pytest.fixture
def member(db, user: User) -> Member:
    return Member.objects.create(
        name="Joao Silva",
        birthday=date(2000, 1, 2),
        user=user,
    )


@pytest.fixture
def authenticated_client(client, user: User):
    client.force_login(user)
    return client


@pytest.fixture
def event(db) -> Event:
    """Evento usado pelo fluxo de check-in via QR (nome fixo no controller)."""
    # Migração 0007 já cria esse evento como seed
    now = timezone.now()
    e, _ = Event.objects.get_or_create(name="Escola Sabatina")
    e.start = now - timedelta(days=30)
    e.end = now + timedelta(days=30)
    e.save()
    TimeScoreRules.objects.create(
        event=e,
        start_time=DAY_START,
        end_time=DAY_END,
        points=50,
    )
    return e


@pytest.fixture
def code(event: Event) -> Code:
    return Code.create_for_event(event)


@pytest.fixture
def expired_code(event: Event) -> Code:
    c = Code.create_for_event(event)
    expire_code(c)
    return c


def expire_code(c: Code) -> None:
    Code.objects.filter(id=c.id).update(
        created_at=timezone.now() - timedelta(seconds=Code.validity_seconds() + 1)
    )
    c.refresh_from_db()