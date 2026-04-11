import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

# Preciso setar essa variável antes de fazer get_asgi_application()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
# Preciso executar get_asgi_application antes de importar qualquer coisa
# do Django
django_asgi_app = get_asgi_application()

from ponto.routing import ws_urlpatterns


application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AuthMiddlewareStack(
            URLRouter(ws_urlpatterns)
        )
})