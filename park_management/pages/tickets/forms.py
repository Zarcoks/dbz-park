from django import forms

from park_management.models import Billet


class AssignBilletForm(forms.Form):
    """
    Le numéro reçu par mail, et rien d'autre : le billet existe déjà en base,
    l'application ne fait que le rattacher au compte de son porteur.
    """
    numero = forms.CharField(
        label="Numéro du billet", max_length=60,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'DBZ-0001'}),
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_numero(self):
        """
        Refuse un numéro inconnu comme un billet déjà pris, sans jamais dire par
        qui : le porteur d'un billet ne regarde pas les comptes des autres.
        """
        numero = self.cleaned_data['numero'].strip()
        try:
            billet = Billet.objects.get(numero=numero)
        except Billet.DoesNotExist:
            raise forms.ValidationError("Aucun billet ne porte ce numéro.")
        if billet.user_id is not None:
            if billet.user_id == getattr(self.user, 'id', None):
                raise forms.ValidationError("Ce billet est déjà sur votre compte.")
            raise forms.ValidationError("Ce billet est déjà assigné à un autre visiteur.")
        # Gardé pour la vue : elle assigne ce billet-là, sans le rechercher deux fois.
        self.billet = billet
        return numero
