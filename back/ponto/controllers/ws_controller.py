import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from ponto.models import Code, Member
from core.settings import LAYER_GROUP

lgr = logging.getLogger(__name__)

class WsController:
    @staticmethod
    async def _emit_new_code(code: Code):
        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            LAYER_GROUP,
            {
                "type": "newCode",
                "code": code.code
            }
        )

    @staticmethod
    async def _emit_member_checkin(member: Member):
        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            LAYER_GROUP,
            {
                "type": "memberCheckin",
                "member": member.name
            }
        )

    @classmethod
    async def async_emit_new_code(cls, code: Code):
        await cls._emit_new_code(code)

    @classmethod
    def sync_emit_new_code(cls, code: Code):
        async_to_sync(cls._emit_new_code)(code)

    @classmethod
    def sync_emit_member_checkin(cls, member: Member):
        async_to_sync(cls._emit_member_checkin)(member)
