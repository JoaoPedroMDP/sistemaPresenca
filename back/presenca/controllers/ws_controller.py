
import logging
from typing import Dict

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from presenca.controllers.code_controller import CodeController
from presenca.models import Code, Member, Event


lgr = logging.getLogger(__name__)


class WsController:
    @staticmethod
    def _get_cl():
        channel_layer = get_channel_layer()
        if not channel_layer:
            lgr.error("Channel layer não foi configurado corretamente.")
            raise RuntimeError("Channel layer não disponível")
        return channel_layer

    @classmethod
    def group_send(cls,group_name, message: Dict):
        async_to_sync(cls._get_cl().group_send)(group_name, message)

    @classmethod
    def send_current_code_for_event(cls, event: Event):
        code = CodeController.get_current_code(event)
        cls._send_code(event, code)

    @classmethod
    def rotate_code_for_event(cls, event: Event):
        code = CodeController.rotate_code(event)
        cls._send_code(event, code)

    @classmethod
    def _send_code(cls, event: Event, code: Code):
        cls.group_send(
            event.as_websocket_group_name(),
            {
                "type": "newCode",
                "code": code.code,
                "expiresAt": code.rotates_at().isoformat()
            }
        )
    
    @classmethod
    def send_member_checkin_for_event(cls, member: Member, event: Event):
        cls.group_send(
            event.as_websocket_group_name(),
            {
                "type": "memberCheckin",
                "member": member.to_checkin()
            }
        )