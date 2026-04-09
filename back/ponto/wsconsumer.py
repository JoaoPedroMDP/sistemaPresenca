import json
import logging

from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from ponto.controllers.ws_controller import WsController
from core.settings import LAYER_GROUP
from ponto.controllers.code_controller import CodeController

lgr = logging.getLogger(__name__)

class WsConsumer(AsyncWebsocketConsumer):
    async def connect(self) -> None:
        lgr.info("Websocket connected")
        await self.channel_layer.group_add(LAYER_GROUP, self.channel_name)
        await self.accept()

        code = await self.get_or_create_code()
        await WsController.async_emit_new_code(code)

    async def disconnect(self, code: int) -> None:
        lgr.info(f"Websocket disconnected: {code}")
        await self.channel_layer.group_discard(LAYER_GROUP, self.channel_name)

    @database_sync_to_async
    def get_or_create_code(self):
        return CodeController.get_unused_code()

    async def newCode(self, event):
        lgr.debug("Received new code event")
        code = event["code"]
        await self.send(text_data=json.dumps({
            "type": "newCode",
            "code": code}))
