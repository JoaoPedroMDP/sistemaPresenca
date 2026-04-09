from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI

from ponto.models import Code, Member
from ponto.api import router as ponto_router


api = NinjaAPI()
api.add_router("/ponto/", ponto_router)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls),
]
