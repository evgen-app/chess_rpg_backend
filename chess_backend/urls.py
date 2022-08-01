from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include, re_path

urlpatterns = (
    [path("api/", include("game.urls"))]
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
)
