from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI

from presenca.api.checkin import checkin_router
from presenca.api.member import member_router
from presenca.api.auth import login_router

api = NinjaAPI()
api.add_router("/checkin/", checkin_router)
api.add_router("/member/", member_router)
api.add_router("/auth/", login_router)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls),
]
