from django.urls import path
from django.urls.conf import include

urlpatterns = [
    path(route="auth/", view=include("djoser.urls.authtoken")),
    path(
        route="",
        view=include("djoser.urls"),
    ),
]
