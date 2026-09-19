import pytest
from django.test import Client as DjangoClient
from django.urls import reverse

from core.models import Client, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def logged_in_client():
    User.objects.create_user(username="vendeur1", password="x", role="vendeur")
    web = DjangoClient()
    web.login(username="vendeur1", password="x")
    return web


def test_creation_reussie(logged_in_client):
    response = logged_in_client.post(
        reverse("client_create"), {"name": "Awa Traoré", "phone": "671 23 45 67"}
    )
    assert response.status_code == 200
    assert Client.objects.filter(phone="+237671234567", name="Awa Traoré").exists()
    assert "créé avec succès" in response.content.decode()


def test_telephone_obligatoire(logged_in_client):
    response = logged_in_client.post(reverse("client_create"), {"name": "Awa Traoré", "phone": ""})
    assert response.status_code == 200
    assert Client.objects.count() == 0
    assert "requis" in response.content.decode()


def test_doublon_normalise_rejete(logged_in_client):
    Client.objects.create(name="Awa Traoré", phone="+237671234567")
    response = logged_in_client.post(
        reverse("client_create"), {"name": "Homonyme éventuel", "phone": "671-23-45-67"}
    )
    assert response.status_code == 200
    assert Client.objects.count() == 1
    assert "existe déjà" in response.content.decode()


def test_deux_homonymes_numeros_differents_acceptes(logged_in_client):
    logged_in_client.post(reverse("client_create"), {"name": "Kouadio Jean", "phone": "671 23 45 67"})
    logged_in_client.post(reverse("client_create"), {"name": "Kouadio Jean", "phone": "690 11 22 33"})

    assert Client.objects.filter(name="Kouadio Jean").count() == 2


def test_creation_refusee_sans_authentification():
    response = DjangoClient().post(
        reverse("client_create"), {"name": "Awa Traoré", "phone": "671 23 45 67"}
    )
    assert response.status_code == 302
    assert Client.objects.count() == 0
