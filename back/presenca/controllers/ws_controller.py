
import logging
from typing import Dict

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from presenca.controllers.code_controller import CodeController
from presenca.models import Member, Event


lgr = logging.getLogger(__name__)


class WsController:
    @staticmethod
    def get_cl():
        channel_layer = get_channel_layer()
        if not channel_layer:
            lgr.error("Channel layer não foi configurado corretamente.")
            raise RuntimeError("Channel layer não disponível")
        return channel_layer

    @classmethod
    def group_send(cls,group_name, message: Dict):
        async_to_sync(cls.get_cl().group_send)(group_name, message)

    @classmethod
    def send_new_code_for_event(cls, event: Event):
        code = CodeController.get_unused_code(event)
        cls.group_send(
            event.as_websocket_group_name(),
            {
                "type": "newCode",
                "code": code.code
            }
        )
    
    @classmethod
    def send_member_checkin_for_event(cls, member: Member, event: Event):
        cls.group_send(
            event.as_websocket_group_name(),
            {
                "type": "memberCheckin",
                "member": {
                    "name": member.name,
                    "photo": member.photo.url if member.photo else None
                }
            }
        )