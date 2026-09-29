from datetime import datetime, timezone as dt_timezone
from decimal import Decimal

import pytest
from django.test import Client as DjangoClient
from django.urls import reverse

from core.models import Client, Sale, SaleLine, User
from core.price_suggestion import get_last_price_for_label

pytestmark = pytest.mark.django_db


@pytest.fixture
def seller():
    return User.objects.create_user(username="vendeur1", password="x", role="vendeur")


def make_sale_with_line(client_obj, seller, label, unit_price, sold_at):
    sale = Sale.objects.create(client=client_obj, seller=seller)
    sale.sold_at = sold_at
    sale.save(update_fields=["sold_at"])
    SaleLine.objects.create(sale=sale, label=label, unit_price=unit_price, quantity=1)
    return sale


def test_dernier_prix_retourne_le_plus_recent(seller):
    client_obj = Client.objects.create(name="Awa Traoré", phone="+237671234567")
    make_sale_with_line(client_obj, seller, "Sac de riz", 15000, datetime(2026, 9, 1, tzinfo=dt_timezone.utc))
    make_sale_with_line(client_obj, seller, "Sac de riz", 17000, datetime(2026, 9, 20, tzinfo=dt_timezone.utc))
    make_sale_with_line(client_obj, seller, "Sac de riz", 16000, datetime(2026, 9, 10, tzinfo=dt_timezone.utc))

    assert get_last_price_for_label("Sac de riz") == Decimal(17000)


def test_aucune_suggestion_sans_vente_anterieure():
    assert get_last_price_for_label("Article jamais vendu") is None


def test_comparaison_sensible_a_la_casse_et_aux_espaces(seller):
    client_obj = Client.objects.create(name="Awa Traoré", phone="+237671234567")
    make_sale_with_line(client_obj, seller, "Sac de riz", 15000, datetime(2026, 9, 1, tzinfo=dt_timezone.utc))

    assert get_last_price_for_label("sac de riz") is None
    assert get_last_price_for_label(" Sac de riz") is None
    assert get_last_price_for_label("Sac de riz ") is None


def test_endpoint_suggestion_prix_refuse_utilisateur_non_authentifie():
    web = DjangoClient()
    response = web.get(reverse("price_suggestion"), {"article": "Sac de riz"})

    assert response.status_code == 302
    assert response.url.startswith(reverse("login"))


def test_endpoint_suggestion_prix_affiche_le_dernier_prix(seller):
    client_obj = Client.objects.create(name="Awa Traoré", phone="+237671234567")
    make_sale_with_line(client_obj, seller, "Sac de riz", 15000, datetime(2026, 9, 1, tzinfo=dt_timezone.utc))

    web = DjangoClient()
    web.login(username="vendeur1", password="x")
    response = web.get(reverse("price_suggestion"), {"article": "Sac de riz"})

    assert response.status_code == 200
    assert "15000" in response.content.decode()


def test_endpoint_suggestion_prix_vide_sans_correspondance(seller):
    web = DjangoClient()
    web.login(username="vendeur1", password="x")
    response = web.get(reverse("price_suggestion"), {"article": "Article jamais vendu"})

    assert response.status_code == 200
    assert response.content.decode().strip() == ""
