from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("api/contact/", views.contact, name="contact"),
    path("api/audit/", views.audit, name="audit"),
]
