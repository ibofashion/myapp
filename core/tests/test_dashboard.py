from datetime import datetime, timezone as dt_timezone
from decimal import Decimal

import pytest
from django.test import Client as DjangoClient
from django.urls import reverse
from django.utils import timezone

from core.dashboard import get_debt_summary, get_payments_total, get_period_bounds
from core.models import Client, Payment, Sale, SaleLine, User
from core.payments import record_payment

pytestmark = pytest.mark.django_db


@pytest.fixture
def seller():
    return User.objects.create_user(username="vendeur1", password="x", role="vendeur")


def make_sale(client_obj, seller, total):
    sale = Sale.objects.create(client=client_obj, seller=seller)
    SaleLine.objects.create(sale=sale, label="Article", unit_price=total, quantity=1)
    return sale


def test_dette_globale_et_par_client_sur_plusieurs_ventes(seller):
    awa = Client.objects.create(name="Awa Traoré", phone="+237671234567")
    ali = Client.objects.create(name="Ali Njoya", phone="+237699000000")

    sale1 = make_sale(awa, seller, 10000)
    make_sale(awa, seller, 5000)
    sale3 = make_sale(ali, seller, 8000)

    record_payment(client=awa, amount=4000, allocations=[(sale1, 4000)], recorded_by=seller)

    total_due, debts_by_client = get_debt_summary()

    assert total_due == Decimal(6000 + 5000 + 8000)
    by_name = {row["client_name"]: row["total_due"] for row in debts_by_client}
    assert by_name == {"Awa Traoré": Decimal(11000), "Ali Njoya": Decimal(8000)}
    assert sale3.client_id == ali.id


def test_dette_globale_nulle_sans_vente_non_soldee(seller):
    client_obj = Client.objects.create(name="Awa Traoré", phone="+237671234567")
    sale = make_sale(client_obj, seller, 10000)
    record_payment(client=client_obj, amount=10000, allocations=[(sale, 10000)], recorded_by=seller)

    total_due, debts_by_client = get_debt_summary()

    assert total_due == Decimal(0)
    assert debts_by_client == []


def test_bornes_du_jour():
    now = datetime(2026, 9, 21, 15, 30, tzinfo=dt_timezone.utc)
    start, end = get_period_bounds("jour", now=now)
    assert start == datetime(2026, 9, 21, 0, 0, tzinfo=dt_timezone.utc)
    assert end == datetime(2026, 9, 22, 0, 0, tzinfo=dt_timezone.utc)


def test_bornes_de_la_semaine():
    # 2026-09-21 est un lundi.
    now = datetime(2026, 9, 24, 8, 0, tzinfo=dt_timezone.utc)
    start, end = get_period_bounds("semaine", now=now)
    assert start == datetime(2026, 9, 21, 0, 0, tzinfo=dt_timezone.utc)
    assert end == datetime(2026, 9, 28, 0, 0, tzinfo=dt_timezone.utc)


def test_bornes_du_mois():
    now = datetime(2026, 9, 21, 8, 0, tzinfo=dt_timezone.utc)
    start, end = get_period_bounds("mois", now=now)
    assert start == datetime(2026, 9, 1, 0, 0, tzinfo=dt_timezone.utc)
    assert end == datetime(2026, 10, 1, 0, 0, tzinfo=dt_timezone.utc)


def test_bornes_du_mois_a_cheval_sur_lannee():
    now = datetime(2026, 12, 15, 8, 0, tzinfo=dt_timezone.utc)
    start, end = get_period_bounds("mois", now=now)
    assert start == datetime(2026, 12, 1, 0, 0, tzinfo=dt_timezone.utc)
    assert end == datetime(2027, 1, 1, 0, 0, tzinfo=dt_timezone.utc)


def test_total_encaisse_sur_periode_avec_paiements_a_cheval(seller):
    client_obj = Client.objects.create(name="Awa Traoré", phone="+237671234567")
    sale = make_sale(client_obj, seller, 100000)

    inside = Payment.objects.create(client=client_obj, amount=3000, recorded_by=seller)
    inside.paid_at = datetime(2026, 9, 21, 10, 0, tzinfo=dt_timezone.utc)
    inside.save(update_fields=["paid_at"])

    also_inside = Payment.objects.create(client=client_obj, amount=2000, recorded_by=seller)
    also_inside.paid_at = datetime(2026, 9, 21, 23, 0, tzinfo=dt_timezone.utc)
    also_inside.save(update_fields=["paid_at"])

    outside = Payment.objects.create(client=client_obj, amount=9000, recorded_by=seller)
    outside.paid_at = datetime(2026, 9, 22, 0, 0, tzinfo=dt_timezone.utc)
    outside.save(update_fields=["paid_at"])

    start, end = get_period_bounds("jour", now=datetime(2026, 9, 21, 12, 0, tzinfo=dt_timezone.utc))
    total = get_payments_total(start, end)

    assert total == Decimal(5000)
    assert sale.id is not None


def test_total_encaisse_nul_sans_paiement_sur_la_periode():
    start, end = get_period_bounds("jour", now=timezone.now())
    assert get_payments_total(start, end) == Decimal(0)


def test_utilisateur_non_authentifie_redirige_vers_connexion():
    web = DjangoClient()
    response = web.get(reverse("dashboard"))

    assert response.status_code == 302
    assert response.url.startswith(reverse("login"))


def test_vendeur_et_admin_voient_les_memes_totaux(seller):
    admin = User.objects.create_user(username="admin1", password="x", role="admin")
    client_obj = Client.objects.create(name="Awa Traoré", phone="+237671234567")
    make_sale(client_obj, seller, 10000)

    vendeur_session = DjangoClient()
    vendeur_session.login(username="vendeur1", password="x")
    vendeur_response = vendeur_session.get(reverse("dashboard"))

    admin_session = DjangoClient()
    admin_session.login(username="admin1", password="x")
    admin_response = admin_session.get(reverse("dashboard"))

    assert vendeur_response.status_code == 200
    assert admin_response.status_code == 200
    assert vendeur_response.context["total_due"] == admin_response.context["total_due"]
    assert vendeur_response.context["payments_total"] == admin_response.context["payments_total"]
    assert vendeur_response.context["debts_by_client"] == admin_response.context["debts_by_client"]


def test_lien_tableau_de_bord_visible_pour_vendeur_et_admin(seller):
    User.objects.create_user(username="admin1", password="x", role="admin")

    vendeur_session = DjangoClient()
    vendeur_session.login(username="vendeur1", password="x")
    vendeur_response = vendeur_session.get(reverse("home"))
    assert "Tableau de bord" in vendeur_response.content.decode()

    admin_session = DjangoClient()
    admin_session.login(username="admin1", password="x")
    admin_response = admin_session.get(reverse("home"))
    assert "Tableau de bord" in admin_response.content.decode()
