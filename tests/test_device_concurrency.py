from __future__ import annotations

import threading

from django.db import connection
import pytest

from presenca.models import Device


@pytest.mark.django_db(transaction=True)
def test_simultaneous_activations_let_only_one_through(device):
    """
        Dois aparelhos lendo o mesmo QR ao mesmo tempo: o UPDATE condicional
        em Device.activate garante que só o primeiro resgate passa.
    """
    threads_count = 4
    barrier = threading.Barrier(threads_count)
    results: list[bool] = []
    errors: list[Exception] = []
    lock = threading.Lock()

    def run():
        try:
            barrier.wait()
            # Cada thread carrega a própria instância, como pedidos separados
            d = Device.objects.get(pk=device.pk)
            ok = d.activate()
            with lock:
                results.append(ok)
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
    assert results.count(True) == 1
    assert Device.objects.get(pk=device.pk).activated_at is not None
