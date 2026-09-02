from django.contrib import admin

from .models import Attraction, AttractionState, Billet

admin.site.register(Billet)
admin.site.register(Attraction)
admin.site.register(AttractionState)
