from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "Agency admin"
admin.site.site_title = "Agency admin"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
]
