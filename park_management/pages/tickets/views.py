import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views import View

from park_management.models import Billet

from .forms import AssignBilletForm

logger = logging.getLogger(__name__)

TEMPLATES = 'park_management/tickets/'


class TicketList(LoginRequiredMixin, View):
    """La page principale : les billets du visiteur connecté, et de quoi en assigner un autre."""

    def get(self, request):
        billets = request.user.billets.all()
        return render(request, TEMPLATES + 'tickets.html',
                      {'billets': billets, 'form': AssignBilletForm(user=request.user)})


class TicketAssign(LoginRequiredMixin, View):
    """Rattache au visiteur connecté un billet déjà créé par la billetterie."""

    def post(self, request):
        form = AssignBilletForm(request.POST, user=request.user)
        if not form.is_valid():
            return render(request, TEMPLATES + 'tickets.html',
                          {'billets': request.user.billets.all(), 'form': form})
        # Le billet est verrouillé le temps de l'assignation : deux visiteurs qui
        # valident le même numéro en même temps ne doivent pas l'obtenir tous les deux.
        with transaction.atomic():
            billet = Billet.objects.select_for_update().get(pk=form.billet.pk)
            if billet.user_id is not None:
                form.add_error('numero', "Ce billet vient d'être assigné à un autre visiteur.")
                return render(request, TEMPLATES + 'tickets.html',
                              {'billets': request.user.billets.all(), 'form': form})
            billet.user = request.user
            billet.assigned_at = timezone.now()
            billet.save()
        logger.info("Le billet " + billet.numero + " a été assigné à " + request.user.username)
        return redirect('tickets')
