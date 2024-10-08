from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

handler404 = "core.views.page_not_found"
handler403 = "core.views.csrf_failure"
handler500 = "core.views.server_error"

urlpatterns = [
    path("", include("posts.urls", namespace="posts")),
    path("admin/", admin.site.urls),
    path("auth/", include("users.urls", namespace="users")),
    path("auth/", include("django.contrib.auth.urls")),
    path("about/", include("about.urls", namespace="about")),
    path("api/v1/", include("api.urls")),
    path(
        "redoc/",
        TemplateView.as_view(template_name="redoc.html"),
        name="redoc",
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
    import debug_toolbar

    urlpatterns += (path("__debug__/", include(debug_toolbar.urls)),)
