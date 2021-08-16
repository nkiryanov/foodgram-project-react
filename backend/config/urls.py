from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from foodgram.core.views import error400, error404, error500

DEBUG = settings.DEBUG
MEDIA_URL = settings.MEDIA_URL
MEDIA_ROOT = settings.MEDIA_ROOT

handler400 = error400
handler404 = error404
handler500 = error500


api_patterns = [
    path("", include("foodgram.users.urls")),
    path("", include("foodgram.recipes.urls")),
]

urlpatterns = [
    path(
        route="admin/",
        view=admin.site.urls,
    ),
    path(
        route="api/",
        view=include(api_patterns),
    ),
] + static(MEDIA_URL, document_root=MEDIA_ROOT)


if DEBUG:
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]
