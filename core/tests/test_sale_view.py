import uuid

import pytest
from django.test import Client as DjangoClient
from django.urls import reverse

from core.models import Client, Sale, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def client_obj():
    return Client.objects.create(name="Awa Traoré", phone="+237671234567")


@pytest.fixture
def logged_in_client():
    User.objects.create_user(username="vendeur1", password="x", role="vendeur")
    web = DjangoClient()
    web.login(username="vendeur1", password="x")
    return web


def formset_data(client_id, key, total=1):
    data = {
        "client": str(client_id),
        "idempotency_key": key,
        "lines-TOTAL_FORMS": str(total),
        "lines-INITIAL_FORMS": "0",
        "lines-MIN_NUM_FORMS": "1",
        "lines-MAX_NUM_FORMS": "1000",
        "lines-0-label": "Sac de riz",
        "lines-0-unit_price": "1500",
        "lines-0-quantity": "3",
    }
    if total > 1:
        data.update({
            "lines-1-label": "Huile",
            "lines-1-unit_price": "2000",
            "lines-1-quantity": "1",
        })
    return data


def test_double_submission_same_idempotency_key_creates_one_sale(client_obj, logged_in_client):
    key = str(uuid.uuid4())
    data = formset_data(client_obj.id, key)

    response1 = logged_in_client.post(reverse("sale_create"), data)
    response2 = logged_in_client.post(reverse("sale_create"), data)

    assert response1.status_code == 200
    assert response2.status_code == 200
    assert Sale.objects.count() == 1


def test_creation_reussie_avec_plusieurs_lignes(client_obj, logged_in_client):
    key = str(uuid.uuid4())
    data = formset_data(client_obj.id, key, total=2)

    response = logged_in_client.post(reverse("sale_create"), data)

    assert response.status_code == 200
    sale = Sale.objects.get()
    assert sale.client_id == client_obj.id
    assert sale.lines.count() == 2
    assert sale.total == 6500


def test_creation_refusee_sans_authentification(client_obj):
    key = str(uuid.uuid4())
    data = formset_data(client_obj.id, key)

    response = DjangoClient().post(reverse("sale_create"), data)

    assert response.status_code == 302
    assert Sale.objects.count() == 0
