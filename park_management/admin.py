from django.contrib import admin

from .models import Attraction, AttractionVisit, Billet, QueueEntry

admin.site.register(Billet)
admin.site.register(Attraction)
admin.site.register(QueueEntry)
admin.site.register(AttractionVisit)
