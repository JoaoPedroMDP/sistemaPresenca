from django.urls import re_path

from presenca.consumer import Consumer

ws_urlpatterns = [
    re_path(r"^ws$", Consumer.as_asgi()),
]