import logging

from asgiref.sync import async_to_sync

from channels.generic.websocket import JsonWebsocketConsumer

from presenca.code_timer import CodeTimerRegistry
from presenca.models import Event
from presenca.controllers.ws_controller import WsController


lgr = logging.getLogger(__name__)


class CustomJsonConsumer(JsonWebsocketConsumer):
    group_name = None

    def add_group(self, event: Event) -> bool:
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
        if self.group_name:
            CodeTimerRegistry.remove_listener(self.group_name)
        self.exit_group()

    def receive_json(self, content, **kwargs):
        type = content.get("type")
        if type == "joinEvent":
            lgr.debug("Mensagem recebida: joinEvent")
            self.join_event(content.get("event"))
        else:
            lgr.warning(f"Tipo de Mensagem desconhecido: {type}")
            self.send_error(f"Tipo de mensagem desconhecido: {type}")

    def join_event(self, event_name):
        """
            Entra no grupo do evento. Nome inexistente ou falha no channel
            layer respondem um evento "error" em vez de derrubar o socket.
        """
        try:
            event = Event.objects.get(name=event_name)
        except Event.DoesNotExist:
            lgr.warning(f"joinEvent para evento inexistente: '{event_name}'")
            self.send_error(f"Evento '{event_name}' não existe. Confira o nome no admin.")
            return

        if not self.add_group(event):
            lgr.error(f"Falha ao adicionar ao evento {event}. Verifique os logs para mais detalhes.")
            self.group_name = None
            self.send_error(f"Não foi possível entrar no evento '{event_name}'.")
            return

        CodeTimerRegistry.add_listener(event)
        WsController.send_current_code_for_event(event)

    def send_error(self, message: str):
        self.send_json({"type": "error", "message": message})

    def newCode(self, event):
        lgr.debug("Mensagem recebida: newCode")
        
        code = event['code']
        self.send_json({
            "type": "newCode",
            "code": code,
            "expiresAt": event["expiresAt"]
        })

    def memberCheckin(self, event):
        lgr.debug("Mensagem recebida: memberCheckin")

        member = event["member"]
        self.send_json({
            "type": "memberCheckin",
            "member": member
        })
