import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from ponto.models import Code
from core.settings import LAYER_GROUP

lgr = logging.getLogger(__name__)

class WsController:
    @staticmethod
    async def _emit_new_code(code: Code):
        channel_layer = get_channel_layer()
        print("Emitting new code")
        lgr.debug("Emitting new code")
        await channel_layer.group_send(
            LAYER_GROUP,
            {
                "type": "newCode",
                "code": code.code
            }
        )
    
    @classmethod
    async def async_emit_new_code(cls, code: Code):
        await cls._emit_new_code(code)
    
    @classmethod
    def sync_emit_new_code(cls, code: Code):
        async_to_sync(cls._emit_new_code)(code)
