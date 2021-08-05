from django.urls import path
from django.urls.conf import include
from rest_framework.routers import DefaultRouter

from .views import CustomUserViewSet

user_router = DefaultRouter()

user_router.register(
    "users",
    CustomUserViewSet,
    basename="users",
)

urlpatterns = [
    path(
        route="auth/",
        view=include("djoser.urls.authtoken"),
    ),
    path(
        route="",
        view=include(user_router.urls),
    ),
]
