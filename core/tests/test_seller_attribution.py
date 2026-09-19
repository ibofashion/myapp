import uuid

import pytest
from django.test import Client as DjangoClient
from django.urls import reverse

from core.models import Client, Payment, Sale, SaleLine, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def client_obj():
    return Client.objects.create(name="Awa Traoré", phone="+237671234567")


@pytest.fixture
def vendeur_connecte():
    user = User.objects.create_user(username="vendeur1", password="x", role="vendeur")
    web = DjangoClient()
    web.login(username="vendeur1", password="x")
    return web, user


def sale_formset_data(client_id, key):
    return {
        "client": str(client_id),
        "idempotency_key": key,
        "lines-TOTAL_FORMS": "1",
        "lines-INITIAL_FORMS": "0",
        "lines-MIN_NUM_FORMS": "1",
        "lines-MAX_NUM_FORMS": "1000",
        "lines-0-label": "Sac de riz",
        "lines-0-unit_price": "1500",
        "lines-0-quantity": "3",
    }


def test_vente_creee_par_vendeur_connecte_lui_est_attribuee(client_obj, vendeur_connecte):
    web, user = vendeur_connecte

    web.post(reverse("sale_create"), sale_formset_data(client_obj.id, str(uuid.uuid4())))

    sale = Sale.objects.get()
    assert sale.seller_id == user.id


def test_paiement_enregistre_par_vendeur_connecte_lui_est_attribue(client_obj, vendeur_connecte):
    web, user = vendeur_connecte
    sale = Sale.objects.create(client=client_obj, seller=user)
    SaleLine.objects.create(sale=sale, label="Article", unit_price=10000, quantity=1)

    web.post(
        reverse("client_detail", args=[client_obj.pk]),
        {
            "amount": "2000",
            f"alloc_{sale.id}": "2000",
            "idempotency_key": str(uuid.uuid4()),
        },
    )

    payment = Payment.objects.get()
    assert payment.recorded_by_id == user.id
