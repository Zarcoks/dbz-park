from django.conf import settings
from django.db import models
from django.templatetags.static import static

# La photo montrée pour une attraction qui n'a pas encore la sienne.
DEFAULT_ATTRACTION_PHOTO = 'attraction-default.svg'

# Un billet donne un rôle au visiteur, du plus commun au plus rare.
ROLE_NORMAL = 'normal'
ROLE_SAYAN = 'sayan'
ROLE_SUPER_SAYAN = 'super_sayan'

ROLE_CHOICES = [
    (ROLE_NORMAL, "Normal"),
    (ROLE_SAYAN, "Saiyan"),
    (ROLE_SUPER_SAYAN, "Super Saiyan"),
]


class Billet(models.Model):
    """
    Un billet d'entrée au parc, sous son numéro et le rôle qu'il donne.

    Les billets ne sont pas créés ici : la billetterie les écrit dans la même
    base, et le visiteur en reçoit le numéro par mail. Un billet existe donc
    avant d'appartenir à quelqu'un, et `user` reste vide jusqu'à ce que son
    porteur l'assigne à son compte depuis l'application.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="visiteur",
                             on_delete=models.SET_NULL, null=True, blank=True,
                             related_name='billets')
    numero = models.CharField("numéro", max_length=60, unique=True)
    role = models.CharField("rôle", max_length=20, choices=ROLE_CHOICES, default=ROLE_NORMAL)
    created_at = models.DateTimeField("créé le", auto_now_add=True)
    assigned_at = models.DateTimeField("assigné le", null=True, blank=True)

    class Meta:
        ordering = ['-assigned_at', '-created_at']

    def __str__(self):
        return "Billet {} ({})".format(self.numero, self.get_role_display())

    def is_assigned(self):
        return self.user_id is not None


class Attraction(models.Model):
    """Une attraction du parc, sous le nombre de visiteurs qu'elle prend à la fois."""
    name = models.CharField("nom", max_length=120)
    photo = models.ImageField("photo", upload_to='attractions/', blank=True)
    max_people = models.PositiveIntegerField("capacité maximale")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_photo_url(self):
        if self.photo:
            return self.photo.url
        return static(DEFAULT_ATTRACTION_PHOTO)


class AttractionState(models.Model):
    """
    L'état d'une attraction à l'instant présent : ce qu'elle porte de monde, et
    combien de temps un tour y dure.

    Une attraction a un seul état, réécrit au fil de l'eau plutôt qu'empilé :
    c'est du direct, pas un historique. `updated_at` dit de quand il date, ce
    qui est la seule façon de savoir qu'une attraction ne répond plus.

    La capacité maximale n'est pas recopiée ici : elle appartient à
    l'attraction, et l'état la lit sur elle (`max_people`). Une seule valeur,
    donc, plutôt que deux qui finiraient par diverger.
    """
    attraction = models.OneToOneField(Attraction, verbose_name="attraction",
                                      on_delete=models.CASCADE, related_name='state')
    current_people = models.PositiveIntegerField("capacité réelle", default=0)
    min_duration = models.DurationField("durée minimale")
    max_duration = models.DurationField("durée maximale")
    updated_at = models.DateTimeField("mis à jour le", auto_now=True)

    class Meta:
        ordering = ['attraction__name']
        verbose_name = "état d'attraction"
        verbose_name_plural = "états d'attraction"

    def __str__(self):
        return "{} : {}/{}".format(self.attraction.name, self.current_people, self.max_people)

    @property
    def max_people(self):
        """La capacité maximale, lue sur l'attraction : l'état ne la tient pas."""
        return self.attraction.max_people

    def free_places(self):
        """
        Les places encore libres, jamais négatives : une attraction qui déborde
        de sa capacité n'a pas moins que zéro place.
        """
        return max(0, self.max_people - self.current_people)

    def is_full(self):
        return self.current_people >= self.max_people

    def occupancy_percent(self):
        """Le remplissage en pourcentage, borné à 100. None si la capacité est nulle."""
        if not self.max_people:
            return None
        return min(100, round(self.current_people / self.max_people * 100))

    def clean(self):
        """Un tour ne peut pas durer moins que son minimum."""
        from django.core.exceptions import ValidationError
        if self.min_duration and self.max_duration and self.min_duration > self.max_duration:
            raise ValidationError({'max_duration': "La durée maximale doit être au moins égale à la minimale."})
