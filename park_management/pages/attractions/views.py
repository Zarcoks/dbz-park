from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View

from park_management.models import Attraction

TEMPLATES = 'park_management/attractions/'


class AttractionList(LoginRequiredMixin, View):
    """Les attractions du parc, telles que le visiteur les voit."""

    def get(self, request):
        return render(request, TEMPLATES + 'attractions.html',
                      {'attractions': Attraction.objects.all()})
