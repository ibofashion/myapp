import pytest
from django.test import Client as DjangoClient
from django.urls import reverse

from core.models import Client

pytestmark = pytest.mark.django_db


def test_creation_reussie():
    response = DjangoClient().post(
        reverse("client_create"), {"name": "Awa Traoré", "phone": "671 23 45 67"}
    )
    assert response.status_code == 200
    assert Client.objects.filter(phone="+237671234567", name="Awa Traoré").exists()
    assert "créé avec succès" in response.content.decode()


def test_telephone_obligatoire():
    response = DjangoClient().post(reverse("client_create"), {"name": "Awa Traoré", "phone": ""})
    assert response.status_code == 200
    assert Client.objects.count() == 0
    assert "requis" in response.content.decode()


def test_doublon_normalise_rejete():
    Client.objects.create(name="Awa Traoré", phone="+237671234567")
    response = DjangoClient().post(
        reverse("client_create"), {"name": "Homonyme éventuel", "phone": "671-23-45-67"}
    )
    assert response.status_code == 200
    assert Client.objects.count() == 1
    assert "existe déjà" in response.content.decode()


def test_deux_homonymes_numeros_differents_acceptes():
    client = DjangoClient()
    client.post(reverse("client_create"), {"name": "Kouadio Jean", "phone": "671 23 45 67"})
    client.post(reverse("client_create"), {"name": "Kouadio Jean", "phone": "690 11 22 33"})

    assert Client.objects.filter(name="Kouadio Jean").count() == 2
