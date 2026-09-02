"""Le choix du billet joué par un visiteur sur une attraction donnée."""


def eligible_billets(user, attraction):
    """
    Les billets du visiteur qui peuvent encore rejoindre cette file : les siens,
    moins ceux qui y tiennent déjà une place ou une présence — on ne fait pas
    deux fois la queue au même endroit.

    Rendus du meilleur rôle au plus commun : c'est le premier qui sera joué.
    """
    return user.billets.exclude(queue_entries__attraction=attraction) \
                       .exclude(visits__attraction=attraction) \
                       .best_role_first()


def best_billet(user, attraction):
    """
    Le billet joué par ce visiteur sur cette attraction : le meilleur de ceux
    qui restent. None quand il n'en a aucun de disponible.

    Un visiteur n'a normalement qu'un billet ; s'il en a plusieurs, c'est le
    meilleur rôle qui sort, sans rien lui demander.
    """
    return eligible_billets(user, attraction).first()
