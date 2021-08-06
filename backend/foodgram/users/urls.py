from django.urls import path
from django.urls.conf import include
from rest_framework.routers import DefaultRouter

from .views import CustomUserViewSet, SubscriptionViewSet

user_router = DefaultRouter()

user_router.register(
    prefix="users/subscriptions",
    viewset=SubscriptionViewSet,
    basename="subscriptions",
)
user_router.register(
    prefix="users",
    viewset=CustomUserViewSet,
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
