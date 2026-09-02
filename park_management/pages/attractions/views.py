import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from park_management.models import Attraction, AttractionVisit, QueueEntry

from .billets import best_billet

logger = logging.getLogger(__name__)

TEMPLATES = 'park_management/attractions/'


def rank_of(entry):
    """Le rang d'une place dans sa file : ceux qui s'y sont inscrits avant, plus un."""
    return entry.attraction.queue_entries.filter(joined_at__lt=entry.joined_at).count() + 1


class AttractionList(LoginRequiredMixin, View):
    """
    Les attractions du parc, et ce que le visiteur y a en cours.

    Chaque carte porte l'un des trois cas : il est dans l'attraction, il tient
    une place dans sa file, ou il peut la rejoindre — avec son meilleur billet,
    sans avoir à le choisir.
    """

    def get(self, request):
        # Les places et les présences du visiteur, retrouvées par attraction en
        # deux requêtes plutôt qu'une par carte.
        entries = {e.attraction_id: e for e in
                   QueueEntry.objects.filter(billet__user=request.user).select_related('attraction', 'billet')}
        visits = {v.attraction_id: v for v in
                  AttractionVisit.objects.filter(billet__user=request.user).select_related('billet')}

        cards = []
        for attraction in Attraction.objects.all():
            entry = entries.get(attraction.id)
            cards.append({
                'attraction': attraction,
                'visit': visits.get(attraction.id),
                'entry': entry,
                'rank': rank_of(entry) if entry and not entry.is_ready else None,
                # Montré avant de rejoindre, pour que le visiteur sache lequel part.
                'billet': best_billet(request.user, attraction) if not entry else None,
            })
        return render(request, TEMPLATES + 'attractions.html', {'cards': cards})


class QueueJoin(LoginRequiredMixin, View):
    """Rejoint la file virtuelle d'une attraction, avec le meilleur billet du visiteur."""

    def post(self, request, attraction_id):
        attraction = get_object_or_404(Attraction, pk=attraction_id)
        billet = best_billet(request.user, attraction)
        if billet is None:
            messages.error(request, "Aucun de vos billets ne peut rejoindre cette file.")
            return redirect('attractions')
        try:
            # La contrainte d'unicité tranche le cas de deux envois simultanés :
            # le second ne crée pas une seconde place.
            QueueEntry.objects.create(attraction=attraction, billet=billet)
        except IntegrityError:
            messages.error(request, "Ce billet est déjà dans la file de cette attraction.")
            return redirect('attractions')
        logger.info("Le billet " + billet.numero + " a rejoint la file de " + attraction.name)
        messages.success(request, "Billet #{} dans la file de {}.".format(billet.numero, attraction.name))
        return redirect('attractions')


class QueueLeave(LoginRequiredMixin, View):
    """
    Quitte la file : la place est rendue, appelée ou non.

    Rien n'est gardé de l'inscription — la file ne tient que le présent, et un
    visiteur qui s'en va n'y a plus sa ligne.
    """

    def post(self, request, entry_id):
        entry = get_object_or_404(QueueEntry.objects.select_related('attraction', 'billet'),
                                  pk=entry_id, billet__user=request.user)
        attraction, numero = entry.attraction, entry.billet.numero
        entry.delete()
        logger.info("Le billet " + numero + " a quitté la file de " + attraction.name)
        messages.success(request, "Vous avez quitté la file de {}.".format(attraction.name))
        return redirect('attractions')


class QueueValidate(LoginRequiredMixin, View):
    """
    Valide une place appelée : le visiteur se présente, et entre.

    La place quitte la file et une présence prend le relais — les deux dans la
    même transaction, pour qu'un billet ne soit jamais dans les deux tables ni
    dans aucune.
    """

    def post(self, request, entry_id):
        # La place doit être celle d'un billet du visiteur : on ne valide pas
        # celle d'un autre, même en connaissant son identifiant.
        entry = get_object_or_404(QueueEntry.objects.select_related('attraction', 'billet'),
                                  pk=entry_id, billet__user=request.user)
        if not entry.is_ready:
            messages.error(request, "Votre tour n'est pas encore venu.")
            return redirect('attractions')
        if entry.ready_expired():
            messages.error(request, "Votre tour est passé : la place a été rendue à la file.")
            return redirect('attractions')

        with transaction.atomic():
            AttractionVisit.objects.create(attraction=entry.attraction, billet=entry.billet)
            entry.delete()
        logger.info("Le billet " + entry.billet.numero + " est entré dans " + entry.attraction.name)
        messages.success(request, "Bienvenue dans {} !".format(entry.attraction.name))
        return redirect('attractions')
