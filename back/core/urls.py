from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI

from presenca.models import Code, Member
from presenca.api import router as ponto_router


api = NinjaAPI()
api.add_router("/presenca/", ponto_router)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls),
]
