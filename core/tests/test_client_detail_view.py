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
def seller():
    return User.objects.create(username="boutique", role="admin")


def make_sale(client_obj, seller, total=10000):
    sale = Sale.objects.create(client=client_obj, seller=seller)
    SaleLine.objects.create(sale=sale, label="Article", unit_price=total, quantity=1)
    return sale


def test_client_sans_vente_affiche_message_absence(client_obj):
    response = DjangoClient().get(reverse("client_detail", args=[client_obj.pk]))
    assert response.status_code == 200
    assert "aucune vente à crédit" in response.content.decode()


def test_liste_des_ventes_avec_solde_et_statut(client_obj, seller):
    make_sale(client_obj, seller, total=10000)
    response = DjangoClient().get(reverse("client_detail", args=[client_obj.pk]))
    content = response.content.decode()
    assert "10000 FCFA" in content
    assert "Non payé" in content


def test_paiement_enregistre_met_a_jour_le_solde_affiche(client_obj, seller):
    sale = make_sale(client_obj, seller, total=10000)
    web = DjangoClient()
    response = web.post(
        reverse("client_detail", args=[client_obj.pk]),
        {
            "amount": "4000",
            f"alloc_{sale.id}": "4000",
            "idempotency_key": str(uuid.uuid4()),
        },
    )
    content = response.content.decode()
    assert response.status_code == 200
    assert Payment.objects.count() == 1
    assert "6000 FCFA" in content
    assert "Partiel" in content


def test_double_soumission_meme_cle_idempotence_ne_cree_quun_paiement(client_obj, seller):
    sale = make_sale(client_obj, seller, total=10000)
    web = DjangoClient()
    key = str(uuid.uuid4())
    data = {"amount": "4000", f"alloc_{sale.id}": "4000", "idempotency_key": key}

    web.post(reverse("client_detail", args=[client_obj.pk]), data)
    web.post(reverse("client_detail", args=[client_obj.pk]), data)

    assert Payment.objects.count() == 1


def test_erreur_validation_affichee_sans_creer_de_paiement(client_obj, seller):
    sale = make_sale(client_obj, seller, total=10000)
    response = DjangoClient().post(
        reverse("client_detail", args=[client_obj.pk]),
        {
            "amount": "10000",
            f"alloc_{sale.id}": "6000",
            "idempotency_key": str(uuid.uuid4()),
        },
    )
    assert response.status_code == 200
    assert Payment.objects.count() == 0
    assert "ne correspond pas" in response.content.decode()
