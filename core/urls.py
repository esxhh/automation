from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("proof-and-demos/", views.proof_demo, name="proof-demo"),
    path("services/<slug:slug>/", views.service_detail, name="service-detail"),
    path("insights/<slug:slug>/", views.insight_detail, name="insight-detail"),
    path("accounts/signup/", views.signup, name="signup"),
    path("accounts/login/", auth_views.LoginView.as_view(
        template_name="core/auth_form.html",
        redirect_authenticated_user=True,
        extra_context={"page_title": "Welcome back", "submit_label": "Sign in"},
    ), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("account/", views.account, name="account"),
    path("api/chat/", views.chat, name="chat"),
    path("api/contact/", views.contact, name="contact"),
    path("api/audit/", views.audit, name="audit"),
]
