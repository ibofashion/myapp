import uuid

import pytest
from django.test import Client as DjangoClient
from django.urls import reverse

from core.models import Client, Payment, Sale, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def client_obj():
    return Client.objects.create(name="Awa Traoré", phone="+237671234567")


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


def test_vente_et_paiement_sur_base_sans_vendeur_reutilisent_un_seul_compte_bootstrap(client_obj):
    assert User.objects.count() == 0

    web = DjangoClient()
    web.post(reverse("sale_create"), sale_formset_data(client_obj.id, str(uuid.uuid4())))

    assert User.objects.count() == 1
    bootstrap_user = User.objects.get()
    assert bootstrap_user.username == "boutique"

    sale = Sale.objects.get()
    assert sale.seller_id == bootstrap_user.id

    web.post(
        reverse("client_detail", args=[client_obj.pk]),
        {
            "amount": "2000",
            f"alloc_{sale.id}": "2000",
            "idempotency_key": str(uuid.uuid4()),
        },
    )

    assert User.objects.count() == 1
    payment = Payment.objects.get()
    assert payment.recorded_by_id == bootstrap_user.id
