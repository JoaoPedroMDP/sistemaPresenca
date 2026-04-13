import logging
from typing import Any
import unicodedata
from asgiref.sync import async_to_sync

from channels.generic.websocket import JsonWebsocketConsumer

from presenca.repositories.event_repository import EventRepository
from presenca.controllers.ws_controller import WsController


lgr = logging.getLogger(__name__)


class CustomJsonConsumer(JsonWebsocketConsumer):
    group_name = None

    def add_group(self, event_name) -> bool:
        event = EventRepository.get(name=event_name)
        if not event:
            lgr.error(f"Evento '{event_name}' não encontrado. Verifique se o nome do evento está correto.")
            return False

        self.group_name = event.as_websocket_group_name()
        try:
            lgr.debug(f"Adicionando {self.channel_name} ao grupo {self.group_name}")
            async_to_sync(self.channel_layer.group_add)(
                self.group_name,
                self.channel_name
            )
            return True
        except TypeError as e:
            lgr.error(f"Erro ao adicionar ao grupo: {e}")
            return False

    def exit_group(self):
        if not self.group_name:
            return

        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )


class Consumer(CustomJsonConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, code):
        lgr.info(f"Websocket disconnected: {code}")
        self.exit_group()

    def receive_json(self, content, **kwargs):
        type = content.get("type")
        if type == "joinEvent":
            lgr.debug("Mensagem recebida: joinEvent")
            event = EventRepository.get(name=content.get("event"))
            success = self.add_group(event)
            if success:
                WsController.send_new_code_for_event(event)
                return
            
            lgr.error(f"Falha ao adicionar ao evento {event}. Verifique os logs para mais detalhes.")

        else:
            lgr.warning(f"Tipo de Mensagem desconhecido: {type}")

    def send_json(self, content: Any, close: bool = False) -> None:
        return super().send_json(content, close)

    def newCode(self, event):
        lgr.debug("Mensagem recebida: newCode")
        
        code = event['code']
        self.send_json({
            "type": "newCode",
            "code": code
        })

    def memberCheckin(self, event):
        lgr.debug("Mensagem recebida: memberCheckin")

        member = event["member"]
        self.send_json({
            "type": "memberCheckin",
            "member": member
        })
