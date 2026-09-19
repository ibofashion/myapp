import pytest
from django.test import Client as DjangoClient
from django.urls import reverse

from core.models import Client, Payment, PaymentAllocation, Sale, SaleLine, User

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


def test_le_vendeur_dorigine_annule_une_vente_sans_allocation(sale):
    web = DjangoClient()
    web.login(username="vendeur1", password="x")

    response = web.post(reverse("sale_delete", args=[sale.pk]))

    assert response.status_code == 302
    assert not Sale.objects.filter(pk=sale.pk).exists()
    assert not SaleLine.objects.filter(sale_id=sale.pk).exists()


def test_un_admin_annule_la_vente_dun_autre_vendeur(sale):
    User.objects.create_user(username="admin1", password="x", role="admin")
    web = DjangoClient()
    web.login(username="admin1", password="x")

    response = web.post(reverse("sale_delete", args=[sale.pk]))

    assert response.status_code == 302
    assert not Sale.objects.filter(pk=sale.pk).exists()


def test_annulation_refusee_si_paiement_impute(sale, client_obj):
    payment = Payment.objects.create(client=client_obj, amount=1000, recorded_by=sale.seller)
    PaymentAllocation.objects.create(payment=payment, sale=sale, amount=1000)

    web = DjangoClient()
    web.login(username="vendeur1", password="x")

    response = web.post(reverse("sale_delete", args=[sale.pk]))

    assert response.status_code == 400
    assert "retirez d" in response.content.decode().lower()
    assert Sale.objects.filter(pk=sale.pk).exists()


def test_un_vendeur_tiers_ne_peut_pas_annuler_la_vente(sale):
    User.objects.create_user(username="vendeur2", password="x", role="vendeur")
    web = DjangoClient()
    web.login(username="vendeur2", password="x")

    response = web.post(reverse("sale_delete", args=[sale.pk]))

    assert response.status_code == 403
    assert Sale.objects.filter(pk=sale.pk).exists()
