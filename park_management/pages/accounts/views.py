import logging

from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.views import View

from .forms import SignupForm

logger = logging.getLogger(__name__)

TEMPLATES = 'park_management/accounts/'


class Signup(View):
    """Création de compte : un visiteur choisit un pseudo et un mot de passe."""

    def get(self, request):
        return render(request, TEMPLATES + 'signup.html', {'form': SignupForm()})

    def post(self, request):
        form = SignupForm(request.POST)
        if not form.is_valid():
            return render(request, TEMPLATES + 'signup.html', {'form': form})
        user = form.save()
        logger.info("Le compte " + user.username + " a été créé")
        login(request, user)
        return redirect('tickets')
