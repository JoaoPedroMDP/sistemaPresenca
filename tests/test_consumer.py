from __future__ import annotations

from asgiref.sync import async_to_sync
from channels.testing import WebsocketCommunicator
import pytest

from presenca.code_timer import CodeTimerRegistry
from presenca.consumer import Consumer
from presenca.models import Event


def _join(event_name: str) -> dict:
    """Abre o socket, manda joinEvent e devolve a primeira resposta."""
    async def run():
        communicator = WebsocketCommunicator(Consumer.as_asgi(), "/ws")
        connected, _ = await communicator.connect()
        assert connected
        await communicator.send_json_to({"type": "joinEvent", "event": event_name})
        response = await communicator.receive_json_from()
        await communicator.disconnect()
        return response

    return async_to_sync(run)()


@pytest.mark.django_db(transaction=True)
def test_join_unknown_event_answers_error_instead_of_crashing():
    response = _join("Evento Que Nao Existe")

    assert response["type"] == "error"
    assert "não existe" in response["message"]


@pytest.mark.django_db(transaction=True)
def test_join_event_with_accents_receives_code():
    event = Event.objects.create(name="Reunião: Louvor & Adoração")

    response = _join(event.name)

    assert response["type"] == "newCode"
    # Thread de rotação encerrada no disconnect
    assert event.as_websocket_group_name() not in CodeTimerRegistry._timers


@pytest.mark.django_db(transaction=True)
def test_unknown_message_type_answers_error():
    async def run():
        communicator = WebsocketCommunicator(Consumer.as_asgi(), "/ws")
        await communicator.connect()
        await communicator.send_json_to({"type": "naoExiste"})
        response = await communicator.receive_json_from()
        await communicator.disconnect()
        return response

    assert async_to_sync(run)()["type"] == "error"


def test_group_name_keeps_only_channels_safe_chars(db):
    event = Event(name="Reunião: Louvor & Adoração")

    assert event.as_websocket_group_name() == "reuniao_louvor_adoracao"


def test_group_name_is_unchanged_for_plain_ascii_names(db):
    assert Event(name="Escola Sabatina").as_websocket_group_name() == "escola_sabatina"
