import pytest
from django.test import Client as DjangoClient

from core.models import User

pytestmark = pytest.mark.django_db


def test_deux_comptes_roles_distincts_se_connectent_independamment():
    User.objects.create_user(username="admin1", password="pass-admin", role="admin")
    User.objects.create_user(username="vendeur1", password="pass-vendeur", role="vendeur")

    admin_client = DjangoClient()
    vendeur_client = DjangoClient()

    assert admin_client.login(username="admin1", password="pass-admin") is True
    assert vendeur_client.login(username="vendeur1", password="pass-vendeur") is True

    assert admin_client.session.session_key != vendeur_client.session.session_key
