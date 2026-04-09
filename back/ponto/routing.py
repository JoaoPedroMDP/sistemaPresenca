from django.urls import re_path

from ponto.wsconsumer import WsConsumer

ws_urlpatterns = [
    re_path(r"^ws$", WsConsumer.as_asgi()),
]