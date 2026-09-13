from core.models import User

BOOTSTRAP_USERNAME = "boutique"


def get_bootstrap_seller() -> User:
    """Retourne l'unique compte vendeur du MVP, le créant si besoin (idempotent)."""
    user, created = User.objects.get_or_create(
        username=BOOTSTRAP_USERNAME,
        defaults={"role": "admin"},
    )
    if created:
        user.set_unusable_password()
        user.save()
    return user
