from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

DEBUG = settings.DEBUG
MEDIA_URL = settings.MEDIA_URL
MEDIA_ROOT = settings.MEDIA_ROOT


extra_patterns = [
    path("", include("foodgram.users.urls")),
]

urlpatterns = [
    path(
        route="admin/",
        view=admin.site.urls,
    ),
    path(
        route="api/",
        view=include(extra_patterns),
    ),
] + static(MEDIA_URL, document_root=MEDIA_ROOT)


if DEBUG:
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]
