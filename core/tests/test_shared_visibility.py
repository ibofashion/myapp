import uuid

import pytest
from django.test import Client as DjangoClient
from django.urls import reverse

from core.models import Client, Sale, User

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


def test_un_vendeur_consulte_une_vente_enregistree_par_un_autre(client_obj):
    User.objects.create_user(username="vendeur1", password="x", role="vendeur")
    User.objects.create_user(username="vendeur2", password="x", role="vendeur")

    web1 = DjangoClient()
    web1.login(username="vendeur1", password="x")
    web1.post(reverse("sale_create"), sale_formset_data(client_obj.id, str(uuid.uuid4())))

    sale = Sale.objects.get()
    assert sale.seller.username == "vendeur1"

    web2 = DjangoClient()
    web2.login(username="vendeur2", password="x")

    client_detail_response = web2.get(reverse("client_detail", args=[client_obj.pk]))
    assert client_detail_response.status_code == 200
    assert "4500 FCFA" in client_detail_response.content.decode()

    sale_detail_response = web2.get(reverse("sale_detail", args=[sale.pk]))
    assert sale_detail_response.status_code == 200
    assert "Sac de riz" in sale_detail_response.content.decode()
