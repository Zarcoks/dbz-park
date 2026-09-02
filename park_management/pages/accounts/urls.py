from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import LoginForm

urlpatterns = [
    path("inscription/", views.Signup.as_view(), name="signup"),
    path("connexion/", auth_views.LoginView.as_view(
        template_name='park_management/accounts/login.html',
        authentication_form=LoginForm), name="login"),
    path("deconnexion/", auth_views.LogoutView.as_view(), name="logout"),
]
