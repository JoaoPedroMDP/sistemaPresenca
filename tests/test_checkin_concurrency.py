from __future__ import annotations

import threading

from django.db import connection
from django.utils import timezone
import pytest

from presenca.controllers.checkin_controller import CheckinController
from presenca.models import CheckIn


@pytest.mark.django_db(transaction=True)
def test_simultaneous_checkins_create_a_single_record(event, member):
    """
        Toque duplo no tablet ou dois scans ao mesmo tempo: o atomic() com
        transaction_mode IMMEDIATE serializa o "verifica e cria".
    """
    threads_count = 4
    barrier = threading.Barrier(threads_count)
    errors: list[Exception] = []

    def run():
        try:
            barrier.wait()
            CheckinController.checkin(member, event, timezone.now())
        except Exception as e:  # noqa: BLE001
            errors.append(e)
        finally:
            connection.close()

    threads = [threading.Thread(target=run) for _ in range(threads_count)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert errors == []
    assert CheckIn.objects.filter(member=member, event=event).count() == 1
