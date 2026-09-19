import pytest
from django.test import Client as DjangoClient
from django.urls import reverse

from core.models import Client, Sale, SaleLine, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def client_obj():
    return Client.objects.create(name="Awa Traoré", phone="+237671234567")


@pytest.fixture
def sale(client_obj):
    seller = User.objects.create_user(username="vendeur1", password="x", role="vendeur")
    sale = Sale.objects.create(client=client_obj, seller=seller)
    SaleLine.objects.create(sale=sale, label="Sac de riz", unit_price=1500, quantity=3)
    return sale


def test_actions_visibles_pour_le_vendeur_proprietaire(sale):
    web = DjangoClient()
    web.login(username="vendeur1", password="x")

    response = web.get(reverse("sale_detail", args=[sale.pk]))

    content = response.content.decode()
    assert "Modifier" in content
    assert "Annuler la vente" in content


def test_actions_visibles_pour_un_admin(sale):
    User.objects.create_user(username="admin1", password="x", role="admin")
    web = DjangoClient()
    web.login(username="admin1", password="x")

    response = web.get(reverse("sale_detail", args=[sale.pk]))

    content = response.content.decode()
    assert "Modifier" in content
    assert "Annuler la vente" in content


def test_actions_absentes_pour_un_vendeur_non_autorise(sale):
    User.objects.create_user(username="vendeur2", password="x", role="vendeur")
    web = DjangoClient()
    web.login(username="vendeur2", password="x")

    response = web.get(reverse("sale_detail", args=[sale.pk]))

    content = response.content.decode()
    assert "Modifier</a>" not in content
    assert "Annuler la vente" not in content
