import uuid

import pytest
from django.test import Client as DjangoClient
from django.test.utils import CaptureQueriesContext
from django.db import connection
from django.urls import reverse

from core.models import Client, Payment, Sale, SaleLine, User
from core.payments import record_payment

pytestmark = pytest.mark.django_db


@pytest.fixture
def client_obj():
    return Client.objects.create(name="Awa Traoré", phone="+237671234567")


@pytest.fixture
def seller():
    return User.objects.create(username="boutique", role="admin")


@pytest.fixture
def logged_in_client(seller):
    seller.set_password("x")
    seller.save()
    web = DjangoClient()
    web.login(username=seller.username, password="x")
    return web


def make_sale(client_obj, seller, total=10000):
    sale = Sale.objects.create(client=client_obj, seller=seller)
    SaleLine.objects.create(sale=sale, label="Article", unit_price=total, quantity=1)
    return sale


def test_client_sans_vente_affiche_message_absence(client_obj, logged_in_client):
    response = logged_in_client.get(reverse("client_detail", args=[client_obj.pk]))
    assert response.status_code == 200
    assert "aucune vente à crédit" in response.content.decode()


def test_liste_des_ventes_avec_solde_et_statut(client_obj, seller, logged_in_client):
    make_sale(client_obj, seller, total=10000)
    response = logged_in_client.get(reverse("client_detail", args=[client_obj.pk]))
    content = response.content.decode()
    assert "10000 FCFA" in content
    assert "Non payé" in content


def test_paiement_enregistre_met_a_jour_le_solde_affiche(client_obj, seller, logged_in_client):
    sale = make_sale(client_obj, seller, total=10000)
    web = logged_in_client
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


def test_double_soumission_meme_cle_idempotence_ne_cree_quun_paiement(client_obj, seller, logged_in_client):
    sale = make_sale(client_obj, seller, total=10000)
    web = logged_in_client
    key = str(uuid.uuid4())
    data = {"amount": "4000", f"alloc_{sale.id}": "4000", "idempotency_key": key}

    web.post(reverse("client_detail", args=[client_obj.pk]), data)
    web.post(reverse("client_detail", args=[client_obj.pk]), data)

    assert Payment.objects.count() == 1


def test_erreur_validation_affichee_sans_creer_de_paiement(client_obj, seller, logged_in_client):
    sale = make_sale(client_obj, seller, total=10000)
    response = logged_in_client.post(
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


def test_acces_refuse_sans_authentification(client_obj):
    response = DjangoClient().get(reverse("client_detail", args=[client_obj.pk]))
    assert response.status_code == 302


def test_client_sans_paiement_affiche_message_historique_vide(client_obj, logged_in_client):
    response = logged_in_client.get(reverse("client_detail", args=[client_obj.pk]))
    assert "Aucun paiement enregistré pour ce client." in response.content.decode()


def test_historique_paiement_impute_sur_une_seule_vente(client_obj, seller, logged_in_client):
    sale = make_sale(client_obj, seller, total=10000)
    record_payment(client=client_obj, amount=4000, allocations=[(sale, 4000)], recorded_by=seller)

    response = logged_in_client.get(reverse("client_detail", args=[client_obj.pk]))
    content = response.content.decode()

    assert "4000 FCFA" in content
    assert f"Vente #{sale.id}" in content
    assert reverse("sale_detail", args=[sale.id]) in content


def test_historique_paiement_reparti_sur_plusieurs_ventes(client_obj, seller, logged_in_client):
    sale1 = make_sale(client_obj, seller, total=5000)
    sale2 = make_sale(client_obj, seller, total=5000)
    record_payment(
        client=client_obj,
        amount=7000,
        allocations=[(sale1, 3000), (sale2, 4000)],
        recorded_by=seller,
    )

    response = logged_in_client.get(reverse("client_detail", args=[client_obj.pk]))
    content = response.content.decode()

    assert "7000 FCFA" in content
    assert f"Vente #{sale1.id}" in content
    assert f"Vente #{sale2.id}" in content
    assert "3000 FCFA" in content
    assert "4000 FCFA" in content


def test_historique_paiements_pas_de_requetes_n_plus_1(client_obj, seller, logged_in_client):
    sale1 = make_sale(client_obj, seller, total=5000)
    sale2 = make_sale(client_obj, seller, total=5000)
    record_payment(client=client_obj, amount=5000, allocations=[(sale1, 5000)], recorded_by=seller)
    record_payment(client=client_obj, amount=5000, allocations=[(sale2, 5000)], recorded_by=seller)

    url = reverse("client_detail", args=[client_obj.pk])
    with CaptureQueriesContext(connection) as baseline:
        logged_in_client.get(url)

    sale3 = make_sale(client_obj, seller, total=5000)
    sale4 = make_sale(client_obj, seller, total=5000)
    record_payment(client=client_obj, amount=5000, allocations=[(sale3, 5000)], recorded_by=seller)
    record_payment(client=client_obj, amount=5000, allocations=[(sale4, 5000)], recorded_by=seller)

    with CaptureQueriesContext(connection) as after_more_payments:
        logged_in_client.get(url)

    assert len(after_more_payments.captured_queries) == len(baseline.captured_queries)
