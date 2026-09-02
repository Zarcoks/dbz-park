import datetime

from django.conf import settings
from django.db import models
from django.templatetags.static import static
from django.utils import timezone

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

# Du meilleur rôle au plus commun. C'est cet ordre qui décide du billet joué
# quand un visiteur en a plusieurs : on sort toujours le meilleur.
ROLE_PRIORITY = [ROLE_SUPER_SAYAN, ROLE_SAYAN, ROLE_NORMAL]


class BilletQuerySet(models.QuerySet):

    def best_role_first(self):
        """
        Les billets du meilleur rôle au plus commun, puis du plus ancien au plus
        récent. Un rôle inconnu passe en dernier plutôt que de fausser l'ordre.
        """
        ranking = models.Case(
            *[models.When(role=role, then=models.Value(rank)) for rank, role in enumerate(ROLE_PRIORITY)],
            default=models.Value(len(ROLE_PRIORITY)),
            output_field=models.IntegerField(),
        )
        return self.annotate(role_rank=ranking).order_by('role_rank', 'created_at')


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

    objects = BilletQuerySet.as_manager()

    class Meta:
        ordering = ['-assigned_at', '-created_at']

    def __str__(self):
        return "Billet {} ({})".format(self.numero, self.get_role_display())

    def is_assigned(self):
        return self.user_id is not None


class Attraction(models.Model):
    """
    Une attraction du parc : ce qu'elle prend de monde à la fois, et combien de
    temps un tour y dure.

    Ce qu'elle porte de visiteurs à l'instant présent ne se lit pas ici mais
    dans les présences (voir AttractionVisit), qui les tiennent une par une.
    """
    name = models.CharField("nom", max_length=120)
    photo = models.ImageField("photo", upload_to='attractions/', blank=True)
    max_people = models.PositiveIntegerField("capacité maximale")
    min_duration = models.DurationField("durée minimale", default=datetime.timedelta(minutes=2))
    max_duration = models.DurationField("durée maximale", default=datetime.timedelta(minutes=5))
    # Combien de secondes on laisse à un billet appelé pour se présenter. Passé
    # ce délai, sa place est prévue pour quelqu'un d'autre : c'est ce qui empêche
    # un visiteur qui ne vient pas de bloquer la file derrière lui.
    max_ready_waiting = models.PositiveIntegerField("tolérance de l'état prêt (secondes)", default=300)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def clean(self):
        """Un tour ne peut pas durer moins que son minimum."""
        from django.core.exceptions import ValidationError
        if self.min_duration and self.max_duration and self.min_duration > self.max_duration:
            raise ValidationError({'max_duration': "La durée maximale doit être au moins égale à la minimale."})

    def duration_range(self):
        """
        La durée d'un tour telle qu'on l'écrit sur une carte : « 2 – 5 min ».

        Les durées de moins d'une minute sont données en secondes plutôt
        qu'arrondies à zéro.
        """
        def written(duration):
            seconds = int(duration.total_seconds())
            if seconds < 60:
                return "{} s".format(seconds)
            return str(round(seconds / 60))

        low, high = written(self.min_duration), written(self.max_duration)
        if low == high:
            return low if low.endswith('s') else "{} min".format(low)
        return "{} – {}{}".format(low, high, "" if high.endswith('s') else " min")

    def get_photo_url(self):
        if self.photo:
            return self.photo.url
        return static(DEFAULT_ATTRACTION_PHOTO)

    def ready_count(self):
        """Les billets déjà appelés, qui n'ont pas encore passé la porte."""
        return self.queue_entries.filter(is_ready=True).count()

    def waiting_count(self):
        """Les billets dans la file qui attendent encore leur tour."""
        return self.queue_entries.filter(is_ready=False).count()

    def ready_tolerance(self):
        """La tolérance de l'état prêt, en durée plutôt qu'en secondes."""
        return datetime.timedelta(seconds=self.max_ready_waiting)

    def expired_ready_entries(self):
        """
        Les places appelées depuis plus longtemps que la tolérance : leurs
        porteurs ne se sont pas présentés, et la place est à donner à un autre.
        """
        deadline = timezone.now() - self.ready_tolerance()
        return self.queue_entries.filter(is_ready=True, ready_at__lt=deadline)

    def people_inside(self):
        """Combien de visiteurs sont dans l'attraction en ce moment."""
        return self.visits.count()

    def free_places(self):
        """
        Les places encore libres, jamais négatives : une attraction qui déborde
        de sa capacité n'a pas moins que zéro place.
        """
        return max(0, self.max_people - self.people_inside())

    def is_full(self):
        return self.people_inside() >= self.max_people


class QueueEntry(models.Model):
    """
    Une place dans la file d'attente virtuelle d'une attraction, tenue par un
    billet : on attend sans faire la queue, et on est appelé le moment venu.

    Une place se lit en deux temps. `joined_at` dit depuis quand le billet
    attend, et son rang dans la file : c'est l'ordre d'inscription qui décide de
    l'ordre d'appel. Puis l'attraction appelle le billet, `is_ready` passe à
    vrai et `ready_at` dit quand — le temps entre les deux est l'attente, et le
    temps depuis `ready_at` est le délai laissé au visiteur pour se présenter.

    La table ne tient que la file du moment : une place disparaît quand son
    porteur entre dans l'attraction (une présence prend le relais, voir
    AttractionVisit) ou qu'il se désiste. D'où un billet au plus par attraction.
    """
    attraction = models.ForeignKey(Attraction, verbose_name="attraction",
                                   on_delete=models.CASCADE, related_name='queue_entries')
    billet = models.ForeignKey(Billet, verbose_name="billet",
                               on_delete=models.CASCADE, related_name='queue_entries')
    joined_at = models.DateTimeField("inscrit le", auto_now_add=True)
    is_ready = models.BooleanField("prêt", default=False)
    ready_at = models.DateTimeField("prêt depuis", null=True, blank=True)

    class Meta:
        # Premier inscrit, premier appelé : l'ordre de la file est celui-là.
        ordering = ['joined_at']
        constraints = [
            models.UniqueConstraint(fields=['attraction', 'billet'],
                                    name='un_billet_une_place_par_attraction'),
        ]
        verbose_name = "place dans la file"
        verbose_name_plural = "places dans les files"

    def __str__(self):
        return "{} – {} ({})".format(self.attraction.name, self.billet.numero,
                                     "prêt" if self.is_ready else "en attente")

    def mark_ready(self):
        """
        Appelle ce billet : il devient prêt, à l'instant où on le dit.

        Ne fait rien sur une place déjà prête : `ready_at` est l'heure du premier
        appel, et la rafraîchir rendrait l'attente plus courte qu'elle ne l'est.
        """
        if self.is_ready:
            return
        self.is_ready = True
        self.ready_at = timezone.now()
        self.save(update_fields=['is_ready', 'ready_at'])

    def waited_for(self):
        """
        Le temps d'attente : jusqu'à l'appel s'il a eu lieu, jusqu'à maintenant
        sinon.
        """
        until = self.ready_at or timezone.now()
        return until - self.joined_at

    def ready_for(self):
        """Depuis combien de temps le billet est appelé, None tant qu'il ne l'est pas."""
        if self.ready_at is None:
            return None
        return timezone.now() - self.ready_at

    def ready_expired(self):
        """
        Le billet a-t-il laissé passer son tour ?

        Vrai quand il est appelé depuis plus longtemps que la tolérance de
        l'attraction : sa place est alors prévue pour quelqu'un d'autre.
        """
        ready_for = self.ready_for()
        if ready_for is None:
            return False
        return ready_for > self.attraction.ready_tolerance()


class AttractionVisit(models.Model):
    """
    Un billet dans une attraction, et depuis quand.

    La table ne tient que le présent, comme la file : la ligne est écrite à
    l'entrée et effacée à la sortie. Ce qu'elle contient est donc, à tout
    moment, la liste de ceux qui se trouvent dans l'attraction.
    """
    attraction = models.ForeignKey(Attraction, verbose_name="attraction",
                                   on_delete=models.CASCADE, related_name='visits')
    billet = models.ForeignKey(Billet, verbose_name="billet",
                               on_delete=models.CASCADE, related_name='visits')
    entered_at = models.DateTimeField("entré le", auto_now_add=True)

    class Meta:
        ordering = ['-entered_at']
        constraints = [
            models.UniqueConstraint(fields=['attraction', 'billet'],
                                    name='un_billet_une_presence_par_attraction'),
        ]
        verbose_name = "présence dans l'attraction"
        verbose_name_plural = "présences dans les attractions"

    def __str__(self):
        return "{} – {} depuis {}".format(self.attraction.name, self.billet.numero,
                                          self.entered_at.strftime("%H:%M"))

    def spent(self):
        """Depuis combien de temps le visiteur est dans l'attraction."""
        return timezone.now() - self.entered_at
