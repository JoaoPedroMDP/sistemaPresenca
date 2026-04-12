from django.urls import re_path

from ponto.consumer import Consumer

ws_urlpatterns = [
    re_path(r"^ws$", Consumer.as_asgi()),
]