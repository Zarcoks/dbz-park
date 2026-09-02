import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from park_management.models import Attraction, AttractionVisit, QueueEntry

logger = logging.getLogger(__name__)

TEMPLATES = 'park_management/console/'


class StaffOnlyMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Réserve une page aux comptes admin.

    Un visiteur qui n'est pas connecté est envoyé sur la connexion ; un visiteur
    connecté sans les droits reçoit un 403, et non la page vide : mieux vaut
    qu'il sache que la porte existe et qu'elle lui est fermée.
    """

    def test_func(self):
        return self.request.user.is_staff


class Console(StaffOnlyMixin, View):
    """
    Le poste de l'admin : qui est appelé, sur quelle attraction, depuis combien
    de temps — et de quoi le faire entrer ou lui rendre sa place.

    Une attraction sans personne d'appelé est montrée quand même : son état (ce
    qu'elle porte, ce qui attend derrière) fait partie de ce qu'on vient voir.
    """

    def get(self, request):
        attractions = []
        for attraction in Attraction.objects.all():
            ready = attraction.queue_entries.filter(is_ready=True) \
                                            .select_related('billet', 'billet__user') \
                                            .order_by('ready_at')
            attractions.append({
                'attraction': attraction,
                'ready': list(ready),
                'inside': attraction.people_inside(),
                'waiting': attraction.waiting_count(),
            })
        return render(request, TEMPLATES + 'console.html', {'attractions': attractions})


class AcceptEntry(StaffOnlyMixin, View):
    """
    Accepte un visiteur appelé : il entre, sa place quitte la file.

    L'admin voit sur sa liste ce que la tolérance dit de la place et décide
    quand même : une place expirée peut être acceptée, c'est le sens du poste.
    """

    def post(self, request, entry_id):
        entry = get_object_or_404(QueueEntry.objects.select_related('attraction', 'billet'),
                                  pk=entry_id, is_ready=True)
        with transaction.atomic():
            AttractionVisit.objects.create(attraction=entry.attraction, billet=entry.billet)
            entry.delete()
        logger.info("Le billet " + entry.billet.numero + " a été accepté dans "
                    + entry.attraction.name + " par " + request.user.username)
        messages.success(request, "Billet #{} accepté dans {}.".format(
            entry.billet.numero, entry.attraction.name))
        return redirect('console')


class RefuseEntry(StaffOnlyMixin, View):
    """Refuse un visiteur appelé : sa place est retirée, la file continue sans lui."""

    def post(self, request, entry_id):
        entry = get_object_or_404(QueueEntry.objects.select_related('attraction', 'billet'),
                                  pk=entry_id, is_ready=True)
        attraction, numero = entry.attraction, entry.billet.numero
        entry.delete()
        logger.info("Le billet " + numero + " a été refusé sur " + attraction.name
                    + " par " + request.user.username)
        messages.success(request, "Billet #{} refusé sur {}.".format(numero, attraction.name))
        return redirect('console')
