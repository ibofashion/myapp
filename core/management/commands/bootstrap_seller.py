from django.core.management.base import BaseCommand

from core.models import User
from core.seller import BOOTSTRAP_USERNAME, get_bootstrap_seller


class Command(BaseCommand):
    help = (
        "Crée (une seule fois) l'unique compte utilisateur du MVP, assigné comme "
        "vendeur de toutes les ventes tant qu'il n'y a pas d'authentification multi-utilisateur (V1)."
    )

    def handle(self, *args, **options):
        already_existed = User.objects.filter(username=BOOTSTRAP_USERNAME).exists()
        get_bootstrap_seller()
        if already_existed:
            self.stdout.write(f"Compte '{BOOTSTRAP_USERNAME}' déjà existant, rien à faire.")
        else:
            self.stdout.write(self.style.SUCCESS(f"Compte '{BOOTSTRAP_USERNAME}' créé (role=admin)."))
